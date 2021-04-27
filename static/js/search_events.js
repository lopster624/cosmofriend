function search_event(event){
    search_ask = event.target.value.toLowerCase()
    for (const element of document.getElementsByClassName('maybe-selected')) {
        console.log(element.childNodes)
        if (!element.childNodes[1].innerText.toLowerCase().includes(search_ask)) {
            element.parentNode.parentNode.classList.add('d-none');
        } else {
            element.parentNode.parentNode.classList.remove('d-none');
        }
    }
}
document.getElementById('search_event').addEventListener('input', search_event);