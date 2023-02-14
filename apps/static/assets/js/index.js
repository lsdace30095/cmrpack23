const exampleModal = document.getElementById('exampleModal')

exampleModal.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget
  const modalTitle = exampleModal.querySelector('.modal-title')
  const modalBodyInput = exampleModal.querySelector('.modal-body input')

})


$("select[name='type']").change(function(){
    var ele = document.getElementById('id_type')

    if(ele[0].selected) {
        $('#input-link').addClass('d-none')
        $('#input-file').removeClass('d-none')
        $('#input-thumbnail').removeClass('d-none')
    }else if(ele[1].selected) {
        $('#input-link').addClass('d-none')
        $('#input-file').removeClass('d-none')
        $('#input-thumbnail').addClass('d-none')
    }else {
        $('#input-link').removeClass('d-none')
        $('#input-file').addClass('d-none')
        $('#input-thumbnail').addClass('d-none')
    }
});
