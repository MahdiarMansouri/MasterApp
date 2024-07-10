document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();
    let fileInput = document.getElementById('file-input');
    let formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Display the uploaded image
    let reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('original-image').src = e.target.result;
        document.getElementById('process-button').style.display = 'block';
    }
    reader.readAsDataURL(fileInput.files[0]);
});

document.getElementById('process-button').addEventListener('click', function () {
    let fileInput = document.getElementById('file-input');
    let formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('segmented-image').src = data.segmented;
                document.getElementById('binary-thresh-image').src = data.binary_thresh;
                document.getElementById('detected-image').src = data.detected;
                document.getElementById('accuracy').textContent = data.accuracy;
                document.getElementById('Spinner_content').style.display = 'none';
            }
        })
        .catch(error => console.error('Error:', error));
});


var Screensize = $(window).width()
if (Screensize >= 1024) {
    $(document).on('click', '.BTN_Upload', function () {
        $('#images').css('display', 'flex');
        $('#original-container').css('display', 'flex');
        $('.Form_content').css('display', 'flex');
    })

    $(document).on('click', '#process-button', function () {
        $('.Spinner_Div').css('display', 'flex');
        $('.container').css('flex-direction', 'row').css('height', '90%');
        $('.Sidebar').css('position', 'sticky').css('left', '0').css('width', '19%').css('height', '95%').css('padding', '0');
        $('#original_container').css('width', '90%');
        $('.main_container').css('width', '79%').css('display', 'flex').css('padding', '0px 10px').css('height', '95%').css('box-shadow', '0 1px 4px rgb(0, 0, 0)').css('border-radius', '10px').css('margin', '0px 10px').css('background-color', '#fff');
        $('.Title_content').css('height', '30%').css('width', '100%').css('display', 'flex');
        $('.Form_content').css('height', '70%').css('display', 'flex');
    })
} else if (Screensize >= 768 && Screensize < 1024) {
    $(document).on('click', '.BTN_Upload', function () {
        $('#images').css('display', 'flex');
        $('#original-container').css('display', 'flex');
        $('.Form_content').css('display', 'flex');
    })
    $(document).on('click', '#process-button', function () {
        $('.Spinner_Div').css('display', 'flex');
        $('.container').css('flex-direction', 'row').css('height', '99%');
        $('.Sidebar').css('width', '99%').css('height', '50%').css('padding', '0');
        $('#original_container').css('width', '90%');
        $('.main_container').css('width', '99%').css('display', 'flex').css('height', '69%').css('box-shadow', '0 1px 4px rgb(0, 0, 0)').css('border-radius', '10px').css('margin', '0px 10px').css('background-color', '#fff');
        $('.Title_content').css('height', '10%').css('width', '100%').css('display', 'flex');
        $('.Form_content').css('height', '70%').css('display', 'flex');
        $('body').removeClass('bodyheight');
    })

} else {
     $(document).on('click', '.BTN_Upload', function () {
        $('#images').css('display', 'flex');
        $('#original-container').css('display', 'flex');
        $('.Form_content').css('display', 'flex');
    })
    $(document).on('click', '#process-button', function () {
        $('.Spinner_Div').css('display', 'flex');
        $('.container').css('flex-direction', 'row').css('height', '99%');
        $('.Sidebar').css('width', '99%').css('height', '50%');
        $('#original_container').css('width', '90%');
        $('.main_container').css('width', '99%').css('display', 'flex').css('height', '69%').css('box-shadow', '0 1px 4px rgb(0, 0, 0)').css('border-radius', '10px').css('margin', '10px 10px').css('background-color', '#fff');
        $('.Title_content').css('height', '10%').css('width', '100%').css('display', 'flex');
        $('.Form_content').css('height', '70%').css('display', 'flex');
        $('body').removeClass('bodyheight');
    })
}

