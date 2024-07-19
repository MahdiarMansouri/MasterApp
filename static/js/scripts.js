document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();
    let fileInput = document.getElementById('file-input');
    let formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Display the uploaded image
    let reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('original-image').src = e.target.result;
        document.getElementById('original-container').style.display = 'block';
        document.getElementById('process-button').style.display = 'block';
    }
    reader.readAsDataURL(fileInput.files[0]);
});

document.getElementById('process-button').addEventListener('click', function () {
    let fileInput = document.getElementById('file-input');
    let formData = new FormData();
    formData.append('file', fileInput.files[0]);

    document.getElementById('spinner_content').style.display = 'flex';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('spinner_content').style.display = 'none';
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('segmented-image').src = data.segmented;
                document.getElementById('binary-thresh-image').src = data.binary_thresh;
                document.getElementById('detected-image').src = data.detected;
                document.getElementById('accuracy').textContent = `${data.accuracy}`;
                document.getElementById('images').style.display = 'flex';
                document.getElementById('main-container').style.display = 'block';
            }
        })
        .catch(error => {
            document.getElementById('spinner_content').style.display = 'none';
            console.error('Error:', error);
        });
});
