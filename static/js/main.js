import { initDragAndDrop } from "./dragdrop.js";
import { handleFormSubmission } from "./form.js";

const textDropzone = document.getElementById("textDropzone");
const imageDropzone = document.getElementById("imageDropzone");
const textFileInput = document.getElementById("textFile");
const imageFileInput = document.getElementById("imageFile");
const imagePreview = document.getElementById("imagePreview");
const wordCountDisplay = document.getElementById("wordCountDisplay");
const wordCountSpan = document.getElementById("wordCount");
const uploadForm = document.getElementById("uploadForm");
const maskColorPicker = document.getElementById("maskColor");
const outputImage = document.getElementById("outputImage");

// Callback for handling text file upload
function handleTextFileUpload(files) {
    const file = files[0];
    if (file.type === "text/plain") {
        assignFileToInput(textFileInput, file);
        const reader = new FileReader();
        reader.onload = (e) => {
            const textContent = e.target.result;
            const wordCount = countWords(textContent);
            wordCountSpan.textContent = wordCount;
            wordCountDisplay.hidden = false;
        };
        reader.readAsText(file);
    } else {
        alert("Please upload a valid text file.");
    }
}

// Callback for handling image file upload
function handleImageFileUpload(files) {
    const file = files[0];
    if (file.type === "image/png") {
        assignFileToInput(imageFileInput, file);
        previewImage(file);
    } else {
        alert("Please upload a valid PNG image file.");
    }
}

// Assign file to the input element programmatically
function assignFileToInput(input, file) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
}

// Preview the uploaded image
function previewImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        imagePreview.hidden = false;
    };
    reader.readAsDataURL(file);
}

// Count words in the text file
function countWords(text) {
    const words = text.split(/\s+/).filter((word) => word.trim().length > 0);
    return words.length;
}

// Initialize drag and drop for text and image files
initDragAndDrop(textDropzone, handleTextFileUpload);
initDragAndDrop(imageDropzone, handleImageFileUpload);

handleFormSubmission(uploadForm, textFileInput, imageFileInput, maskColorPicker, outputImage);
