function getTextContent(elem) {
    if (elem.textContent) {
        return elem.textContent;
    } else {
        return elem.innerText;
    }
}
