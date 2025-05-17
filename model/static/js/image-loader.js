// @ts-nocheck
// Fonction pour gérer les erreurs de chargement d'images
function handleImageErrors() {
  document.addEventListener("DOMContentLoaded", function () {
    // Sélectionner toutes les images qui sont des résultats d'analyse
    const resultImages = document.querySelectorAll(
      ".results-image img, .mole-card img"
    );

    resultImages.forEach((img) => {
      img.onerror = function () {
        console.error("Erreur de chargement d'image:", this.src);

        // Tenter de reconstruire l'URL avec un autre chemin
        if (this.src.includes("/uploads/")) {
          // Récupérer juste le nom du fichier
          const filename = this.src.split("/").pop();

          // Essayer avec un chemin alternatif
          const newSrc = `/uploads/${filename}`;
          console.log("Tentative avec une URL alternative:", newSrc);

          if (this.src !== newSrc) {
            this.src = newSrc;
          } else {
            // Si l'URL alternative est la même, montrer une image par défaut
            this.src = "/static/img/image-error.svg";
            this.alt = "Image non disponible";
          }
        }
      };
    });
  });
}

// Exécuter la fonction
handleImageErrors();
