function show_fields() {
    const elem = document.getElementById('btnradio5');
    if (elem.checked) {
        document.getElementById('date_fields').classList.remove('d-none');
    } else {
        document.getElementById('date_fields').classList.add('d-none');
    }
}

function submit_form() {
    let form = document.getElementById('form');
    form.submit();
}

document.getElementById('radio_fields').addEventListener('click', show_fields);