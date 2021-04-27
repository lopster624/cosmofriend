function select(event) {
        if (event.target === this.childNodes[1]) {
            return;
        }
        this.childNodes[1].checked = !this.childNodes[1].checked;
    }

let selectedAll = false;
function selectAll() {
    this.innerText = selectedAll ? 'Выбрать всех' : 'Отменить выбор всех';
    selectedAll = !selectedAll;
    for (const element of document.getElementsByClassName('maybe-selected')) {
        element.childNodes[1].checked = selectedAll;
    }
}
function searchAll(event){
    search_ask = event.target.value.toLowerCase()
    for (const element of document.getElementsByClassName('maybe-selected')) {
        if (!element.childNodes[element.childNodes.length-2].innerText.toLowerCase().includes(search_ask)) {
            element.classList.add('d-none');
        } else {
            element.classList.remove('d-none');
        }
    }
}

document.getElementById('search_name').addEventListener('input', searchAll);
document.getElementById('select-all').addEventListener('click', selectAll);
for (const element of document.getElementsByClassName('maybe-selected')) {
    element.addEventListener('click', select);
}