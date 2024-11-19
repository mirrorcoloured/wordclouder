export async function handleFormSubmission(
    uploadForm,
    textFileInput,
    imageFileInput,
    maskColorPicker,
    outputImage
) {
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Validate file inputs
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
        formData.append("mask_color", maskColorPicker.value);

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
}
