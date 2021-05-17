function searchAll(event){
    search_ask = event.target.value.toLowerCase()
    for (const element of document.getElementsByClassName('maybe-selected')) {
        if (!element.childNodes[element.childNodes.length-2].childNodes[3].innerText.toLowerCase().includes(search_ask)) {
            element.classList.add('d-none');
        } else {
            element.classList.remove('d-none');
        }
    }
}

document.getElementById('search_name').addEventListener('input', searchAll);