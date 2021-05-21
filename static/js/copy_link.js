function copy_link() {
    const copyText = document.getElementById("link_input");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
}