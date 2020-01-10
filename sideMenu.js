/*
--------------------------------------------------
* Vars
*/

const
	root = document.documentElement,

	colorMenuContent = document.getElementById("colorMenuContent"),
	scaleMenuContent = document.getElementById("scaleMenuContent"),
	sideMenuFrame = document.getElementById("sideMenuFrame"),

	sideMenuBoxes = sideMenuFrame.getElementsByClassName("menuBox"),
	sideMenuTabs = sideMenuFrame.getElementsByClassName("menuTab"),

	colorInputs = [].slice.call(colorMenuContent.querySelectorAll("input")),
	scaleButton = [].slice.call(scaleMenuContent.querySelectorAll("button")),
	scaleInput = [].slice.call(scaleMenuContent.querySelectorAll("input")),
	
	tocButton = document.getElementById("close_tab"),

	transitionSpeed = 300
	;

/*
--------------------------------------------------
* Menu Event Processing
*/

function sideMenuPoke() {
	let sideMenuActiveTag = this.classList.contains("active");	
	if(!sideMenuFrame.classList.contains("active")) sideMenuToggle();
	if(sideMenuActiveTag) {
		sideMenuToggle();
		setTimeout(sideMenuActiveBoxSwap, transitionSpeed);
	} else {
		sideMenuActiveBoxSwap();
		sideMenuActiveTabSwap();
		this.parentNode.classList.add("active");
		this.classList.add("active");
	}
}

function sideMenuToggle() {
	sideMenuFrame.classList.toggle("active");
	sideMenuActiveTabSwap();
}

function sideMenuActiveBoxSwap() {
	Array.from(sideMenuBoxes).forEach(function(el) {
		el.classList.remove("active");
	});
}

function sideMenuActiveTabSwap() {
	Array.from(sideMenuTabs).forEach(function(el) {
		el.classList.remove("active");
	});
}

/*
--------------------------------------------------
* Close menu after clicking navagation link
*/
function tocButtonClose() {
    sideMenuToggle();
    setTimeout(sideMenuActiveBoxSwap, transitionSpeed);
}

/*
--------------------------------------------------
* Color Wheel
*/

function colorHandleUpdate(e) {
    if (this.id === "red") root.style.setProperty("--red", this.value);
    if (this.id === "green") root.style.setProperty("--green", this.value);
	if (this.id === "blue") root.style.setProperty("--blue", this.value);
}

/*
--------------------------------------------------
* Text Scaling
*/

function scaleHandleApply(e) {
    root.style.setProperty("--fontSizeMod", scaleInput[0].value);
}

function scaleHandleUpdate(e) {
    root.style.setProperty("--fontSizeModPreview", scaleInput[0].value);
}

/*
--------------------------------------------------
* Initialization
*/

function sideMenuEnable() {
	Array.from(sideMenuTabs).forEach(function(el) {
		el.addEventListener("click", sideMenuPoke);
	});
	setTimeout(function() {
		document.documentElement.classList.remove("no-js");
	}, transitionSpeed)
	colorInputs.forEach(input => input.addEventListener("change", colorHandleUpdate));
	colorInputs.forEach(input => input.addEventListener("mousemove", colorHandleUpdate));
	scaleButton.forEach(input => input.addEventListener("click", scaleHandleApply));
	scaleInput.forEach(input => input.addEventListener("change", scaleHandleUpdate));
	scaleInput.forEach(input => input.addEventListener("mousemove", scaleHandleUpdate));
    tocButton.addEventListener("click", tocButtonClose);
}

sideMenuEnable();
