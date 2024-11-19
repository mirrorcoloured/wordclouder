const uploadForm = document.getElementById("uploadForm");
const dropzone = document.getElementById("dropzone");
const textFileInput = document.getElementById("textFile");
const imageFileInput = document.getElementById("imageFile");
const imagePreview = document.getElementById("imagePreview");
const outputImage = document.getElementById("outputImage");
const backgroundColorPicker = document.getElementById("backgroundColor");

let dragCounter = 0;

// Drag-and-drop functionality
dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragging");
});

dropzone.addEventListener("dragleave", () => {
    dragCounter--;
    if (dragCounter === 0) {
        dropzone.classList.remove("dragging");
    }
});

dropzone.addEventListener("dragenter", () => {
    dragCounter++;
    dropzone.classList.add("dragging");
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragging");
    dragCounter = 0;

    const files = e.dataTransfer.files;
    for (const file of files) {
        if (file.type === "text/plain") {
            assignFileToInput(textFileInput, file);
        } else if (file.type === "image/png") {
            assignFileToInput(imageFileInput, file);
            previewImage(file);
        }
    }
});

// Assign file to the input element programmatically
function assignFileToInput(input, file) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
}

// Preview the uploaded image
imageFileInput.addEventListener("change", () => {
    if (imageFileInput.files.length > 0) {
        previewImage(imageFileInput.files[0]);
    }
});

function previewImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        imagePreview.hidden = false;
    };
    reader.readAsDataURL(file);
}

// Handle form submission
uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Validate that both files have been uploaded
    if (!textFileInput.files.length) {
        alert("Please upload a text file.");
        return;
    }

    if (!imageFileInput.files.length) {
        alert("Please upload an image file.");
        return;
    }

    const formData = new FormData();
    formData.append("text_file", textFileInput.files[0]);
    formData.append("image_file", imageFileInput.files[0]);
    formData.append("background_color", backgroundColorPicker.value);

    const response = await fetch("/process/", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        outputImage.src = url;
        outputImage.hidden = false;
    } else {
        alert("Error generating word cloud. Please try again.");
    }
});
