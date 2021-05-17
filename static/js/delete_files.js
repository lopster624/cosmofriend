function put_pic_id(data) {
    let elem = document.getElementById('delete_photos');
    elem.value += ' ' + data;
    document.getElementById(data).classList.add('d-none');

}

function put_vid_id(data) {
    let elem = document.getElementById('delete_videos');
    elem.value += ' ' + data;
    document.getElementById(data).classList.add('d-none');
}
