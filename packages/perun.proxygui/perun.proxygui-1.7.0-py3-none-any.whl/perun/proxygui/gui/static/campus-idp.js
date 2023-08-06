function hideElement(element) {
	element.classList.add("vhide", "d-none");
}

function showElement(element) {
	element.classList.remove("vhide", "d-none");
}

function showMoreOptions(showButton) {
	document
		.getElementById(showButton.dataset.targetform)
		.querySelectorAll(".idp-hidden")
		.forEach(showElement);
	hideElement(showButton);
}

function selectizeScore() {
	return function () {
		return 1;
	};
}

function selectizeRenderOption(item, escape) {
	var escapedText = escape(item.text);
	var escapedImage = escape(item.image);

	var is_muni_framework = document.body.classList.contains("framework_muni");

	if (is_muni_framework) {
		return (
			'<div class="box-vcards-list__item box-vcard--compact searchbox-result u-pr-0 u-pl-0">' +
			'<div class="box-vcards-list__inner u-pr-0 u-pl-0">' +
			'<p class="box-vcards-list__img center">' +
			'<img src="' +
			escapedImage +
			'" class="img-searchbox" alt=""/>' +
			"</p>" +
			'<div class="box-vcards-list__content u-pb-0 u-pt-0 u-pr-0 u-pl-10">' +
			escapedText +
			"</div>" +
			"</div>" +
			"</div>"
		);
	} else {
		return (
			'<div class="list-group-item list-group-item-action d-flex align-items-center">' +
			'<p class="mb-0">' +
			'<img src="' +
			escapedImage +
			'" class="img-searchbox" alt=""/>' +
			"</p>" +
			'<div class="margin-left-24">' +
			escapedText +
			"</div>" +
			"</div>"
		);
	}
}

function selectizeOnChange(value) {
	$(this["$input"]).closest("form").trigger("submit");
}

function selectizeLoad(query, callback) {
	if (!query.length) {
		return callback();
	}

	this.clearCache("option");
	this.clearOptions();
	this.refreshOptions(true);

	$.ajax({
		url: "./idpSearch.php",
		type: "GET",
		dataType: "json",
		data: {
			q: query,
			index: this.settings.myIndex,
			idphint: this.settings.idphint,
			language: document.documentElement.getAttribute("lang"),
			page_limit: 10,
		},
		error: function () {
			callback();
		},
		success: function (res) {
			callback(res.items);
		},
	});
}

document.addEventListener("DOMContentLoaded", function () {
	var moreOptions = document.querySelectorAll(".more-options");
	if (moreOptions) {
		moreOptions.forEach(function (showButton) {
			showButton.addEventListener(
				"click",
				showMoreOptions.bind(null, showButton)
			);
		});
	}

	var password = document.getElementById("password");
	var togglePassword = document.getElementById("toggle-password");
	if (password && togglePassword) {
		password.addEventListener("keyup", function (event) {
			var message = document.getElementById("capslock-warning");
			var wrapper = document.getElementById("capslock-warning-wrapper");
			var isCapsLock = event.getModifierState("CapsLock");
			if (isCapsLock) {
				showElement(message);
			} else {
				hideElement(message);
			}
			if (wrapper) {
				wrapper.classList.toggle("warning", isCapsLock);
			}
		});

		togglePassword.addEventListener("click", function () {
			var type =
				password.getAttribute("type") === "password" ? "text" : "password";
			password.setAttribute("type", type);

			this.classList.toggle("icon-eye-slash");
			this.querySelector("i").classList.toggle("fa-eye");
			this.querySelector("i").classList.toggle("fa-eye-slash");
		});
	}

	document.querySelectorAll(".remove-option").forEach(function (element) {
		element.addEventListener("click", function (e) {
			e.stopPropagation();

			let button = this.parentElement.parentElement;

			$.ajax({
				url: "./removeCookie.php",
				type: "POST",
				data: {
					entityid: button.value,
				},
			});

			button.remove();
		});
	});

	document.querySelectorAll(".idps-form-nojs-div").forEach(hideElement);
	document.querySelectorAll(".idps-form-div").forEach(showElement);

	var indexes = JSON.parse(
		document.querySelector('meta[name="searchbox-indexes"]').content
	);
	var placeholderTexts = JSON.parse(
		document.querySelector('meta[name="searchbox-placeholders"]').content
	);
	var defaultPlaceholder = document.querySelector(
		'meta[name="searchbox-default"]'
	).content;
	var is_muni_framework = document.body.classList.contains("framework_muni");
	indexes.forEach(function (index) {
		$("#searchbox-" + index).selectize({
			valueField: "idpentityid",
			labelField: "text",
			options: [],
			create: false,
			maxItems: 1,
			myIndex: index,
			idphint: JSON.parse(
				document.querySelector('meta[name="idphint"]').content
			),
			loadThrottle: 250,
			placeholder: placeholderTexts[index] ?? defaultPlaceholder,
			render: {
				option: selectizeRenderOption,
			},
			onChange: selectizeOnChange,
			score: selectizeScore,
			load: selectizeLoad,
		});
		if (is_muni_framework) {
			$("#searchbox-" + index + "-selectized").after(
				'<span class="icon icon-search"></span>'
			);
			$("#searchbox-" + index + "-selectized")
				.parent()
				.addClass("inp-fix inp-icon inp-icon--after");
		}
	});
});
