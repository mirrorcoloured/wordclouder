// Initialize drag and drop for the specified element
export function initDragAndDrop(element, callback) {
    let dragCounter = 0;

    element.addEventListener("dragover", (e) => {
        e.preventDefault();
        element.classList.add("dragging");
    });

    element.addEventListener("dragleave", () => {
        dragCounter--;
        if (dragCounter === 0) {
            element.classList.remove("dragging");
        }
    });

    element.addEventListener("dragenter", () => {
        dragCounter++;
        element.classList.add("dragging");
    });

    element.addEventListener("drop", (e) => {
        e.preventDefault();
        element.classList.remove("dragging");
        dragCounter = 0;

        const files = e.dataTransfer.files;
        callback(files);
    });
}
