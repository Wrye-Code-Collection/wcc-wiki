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
    fontSizeMod = getComputedStyle(document.documentElement).getPropertyValue('--fontSizeMod'),

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
    // existing code
    root.style.setProperty("--fontSizeMod", scaleInput[0].value);
    // added code
    SetCookie("fontSizeVar=", scaleInput[0].value, 30);
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

function SetCookie(name,value,days) {
    var now= new Date();
    var expDate = new Date();
    if (days==null || days==0) days=1;
    //create date after no of "days" from now
    expDate.setTime(now.getTime() + 3600000*24*days);
 
    //create cookie with name, value and expire date
    document.cookie = name + escape(value)+";expires="+expDate.toUTCString();
}

function ReadCookie(name) {
    if (name == "") return "";
    var strCookie =" " + document.cookie;
    var idx = strCookie.indexOf(" " + name + "=");
    if (idx == -1) idx = strCookie.indexOf(";" + name + "=");
    if (idx == -1) return "";

    var idx1 = strCookie.indexOf(";", idx+1);
    if (idx1 == -1) idx1 = strCookie.length; 
    return unescape(strCookie.substring(idx + name.length+2, idx1));
}

sideMenuEnable();

window.addEventListener('load', () => document.documentElement.style.setProperty('--fontSizeMod', ReadCookie('fontSizeVar')));
