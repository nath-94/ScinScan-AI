  const openCameraBtn = document.getElementById("open-camera-btn");
  const cameraModal = document.getElementById("camera-modal");
  const video = document.getElementById("video");
  const takePhotoBtn = document.getElementById("take-photo-btn");
  const closeCameraBtn = document.getElementById("close-camera-btn");
  const canvas = document.getElementById("canvas");
  const fileInput = document.getElementById("file-input");
  const previewImage = document.getElementById("preview-image");

  let stream = null;

  if (openCameraBtn) {
    openCameraBtn.onclick = async function () {
      cameraModal.style.display = "flex";
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
    };
  }

  if (closeCameraBtn) {
    closeCameraBtn.onclick = function () {
      cameraModal.style.display = "none";
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }

if (takePhotoBtn) {
    takePhotoBtn.onclick = function () {
      canvas
        .getContext("2d")
        .drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(function (blob) {
        const file = new File([blob], "photo.jpg", { type: "image/jpeg" });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;

        // AJOUT ICI
        if (fileInput.files.length) {
          handleFiles(fileInput.files);
        }

        const url = URL.createObjectURL(blob);
        if (previewImage) previewImage.src = url;

        cameraModal.style.display = "none";
        if (stream) {
          stream.getTracks().forEach((track) => track.stop());
        }
        fileInput.dispatchEvent(new Event("change"));
      }, "image/jpeg");
    };
}
