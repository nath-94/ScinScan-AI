// @ts-nocheck
document.addEventListener("DOMContentLoaded", function () {
  // Éléments DOM
  const fileInput = document.getElementById("file-input");
  const uploadArea = document.getElementById("upload-area");
  const fileInfo = document.getElementById("file-info");
  const previewImage = document.getElementById("preview-image");
  const removeImageBtn = document.getElementById("remove-image");
  const analyzeBtn = document.getElementById("analyze-btn");
  const uploadStatus = document.getElementById("upload-status");
  const spinner = document.getElementById("spinner");
  const statusMessage = document.getElementById("status-message");
  const resultsSection = document.getElementById("results-section");
  const newAnalysisBtn = document.getElementById("new-analysis-btn");

  // Éléments de résultat
  const resultImage = document.getElementById("result-image");
  const resultClassName = document.getElementById("result-class-name");
  const resultClassDescription = document.getElementById(
    "result-class-description"
  );
  const resultRisk = document.getElementById("result-risk");
  const resultConfidence = document.getElementById("result-confidence");
  const resultRecommendation = document.getElementById("result-recommendation");

  // Variables
  let selectedFile = null;
  let chart = null;

  // Événements pour l'upload par drag & drop
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    uploadArea.addEventListener(eventName, unhighlight, false);
  });

  function highlight() {
    uploadArea.classList.add("highlight");
  }

  function unhighlight() {
    uploadArea.classList.remove("highlight");
  }

  // Gérer le dépôt de fichier
  uploadArea.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length) {
      handleFiles(files);
    }
  }

  // Gérer la sélection de fichier via le bouton
  fileInput.addEventListener("change", function () {
    if (this.files.length) {
      handleFiles(this.files);
    }
  });

  // Gérer les fichiers sélectionnés
  function handleFiles(files) {
    selectedFile = files[0];
    fileInfo.textContent = selectedFile.name;

    // Afficher l'aperçu de l'image
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImage.src = e.target.result;
      uploadArea.classList.add("has-image");
      analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(selectedFile);
  }

  // Bouton pour supprimer l'image
  removeImageBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    resetUpload();
  });

  function resetUpload() {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.textContent = "Aucun fichier sélectionné";
    previewImage.src = "";
    uploadArea.classList.remove("has-image");
    analyzeBtn.disabled = true;
    uploadStatus.classList.remove("active");
    statusMessage.textContent = "";
    statusMessage.classList.remove("error", "success");
  }

  // Analyser l'image
  analyzeBtn.addEventListener("click", function () {
    if (!selectedFile) return;

    // Afficher le statut du chargement
    uploadStatus.classList.add("active");
    statusMessage.textContent = "Analyse en cours...";
    statusMessage.classList.remove("error", "success");

    // Créer un FormData
    const formData = new FormData();
    formData.append("file", selectedFile);

    // Envoyer la requête AJAX
    fetch("/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Mettre à jour le statut
          statusMessage.textContent = "Analyse terminée avec succès!";
          statusMessage.classList.add("success");

          // Option 1: Afficher les résultats dans la même page
          displayResults(data);

          // Option 2: Stocker les résultats et rediriger vers la page de résultats
          // Stockage des résultats dans localStorage pour utilisation dans la page de résultats
          localStorage.setItem("skinScanResult", JSON.stringify(data));

          // Redirection vers la page de résultats (décommentez pour utiliser)
          // window.location.href = '/result';
        } else {
          // Afficher l'erreur
          statusMessage.textContent = "Erreur: " + data.error;
          statusMessage.classList.add("error");
        }
      })
      .catch((error) => {
        console.error("Erreur:", error);
        statusMessage.textContent =
          "Erreur lors de l'analyse. Veuillez réessayer.";
        statusMessage.classList.add("error");
      })
      .finally(() => {
        // Masquer le spinner après un court délai
        setTimeout(() => {
          uploadStatus.classList.remove("active");
        }, 2000);
      });
  });

  // Afficher les résultats
  function displayResults(data) {
    // Mettre à jour l'image - utiliser l'image annotée si disponible
    resultImage.src = data.annotated_image || data.file_url;
    // S'assurer que l'image se charge correctement
    resultImage.onerror = function () {
      console.error("Erreur de chargement de l'image:", this.src);
      // Essayer avec l'URL alternative si disponible
      if (this.src === data.annotated_image && data.file_url) {
        console.log("Tentative avec l'URL alternative:", data.file_url);
        this.src = data.file_url;
      }
    };

    // Vérifier si l'image contient des grains de beauté à risque élevé
    const hasHighRisk = data.has_high_risk;
    const hasMultipleMoles = data.analyzed_moles > 1;

    // Si risque élevé détecté et plusieurs grains de beauté, afficher uniquement la recommandation
    if (hasMultipleMoles) {
      // Cacher les éléments de diagnostic détaillé
      document.querySelector(".result-primary").style.display = "none";
      document.querySelector(".result-details").style.display = "none";
      document.querySelector(".results-chart").style.display = "none";

      // Mettre en évidence la recommandation
      if (hasHighRisk) {
        resultRecommendation.innerHTML =
          "<strong>ATTENTION:</strong> Un ou plusieurs grains de beauté présentent un risque élevé. \n" +
          data.recommendation;
        resultRecommendation.style.fontSize = "1.2em";
        resultRecommendation.style.color = "#d9534f";
      } else {
        resultRecommendation.innerHTML =
          "<strong>Recommandation:</strong> " + data.recommendation;
        resultRecommendation.style.fontSize = "1.2em";
        resultRecommendation.style.color = "#5bc0de";
      }
      // Mettre en évidence le bouton de détails
      const viewDetailsBtn = document.getElementById("view-details-btn");
      if (viewDetailsBtn) {
        viewDetailsBtn.classList.remove("btn-secondary");
        viewDetailsBtn.classList.add("btn-info");
        viewDetailsBtn.innerHTML =
          '<i class="fas fa-search-plus"></i> Voir l\'analyse détaillée';
      }
    } else {
      // Affichage normal pour un seul grain de beauté ou risque faible
      document.querySelector(".result-primary").style.display = "block";
      document.querySelector(".result-details").style.display = "block";
      document.querySelector(".results-chart").style.display = "block";

      // Mettre à jour les informations du diagnostic
      resultClassName.textContent =
        data.class_full_name + " (" + data.class_name + ")";
      resultClassDescription.textContent = data.class_description;

      // Mettre à jour le niveau de risque avec la bonne classe
      resultRisk.textContent = data.class_risk;
      resultRisk.className = "badge";

      if (data.class_risk.includes("Très faible")) {
        resultRisk.classList.add("badge-success");
      } else if (data.class_risk.includes("Modéré")) {
        resultRisk.classList.add("badge-warning");
      } else {
        resultRisk.classList.add("badge-danger");
      }

      // Mettre à jour la confiance
      resultConfidence.textContent = (data.confidence * 100).toFixed(1) + "%";

      // Mettre à jour la recommandation (format normal)
      resultRecommendation.textContent = data.recommendation;
      resultRecommendation.style.fontSize = "";
      resultRecommendation.style.color = "";

      // Réinitialiser le style du bouton de détails
      const viewDetailsBtn = document.getElementById("view-details-btn");
      if (viewDetailsBtn) {
        viewDetailsBtn.classList.remove("btn-info");
        viewDetailsBtn.classList.add("btn-secondary");
        viewDetailsBtn.innerHTML =
          '<i class="fas fa-search-plus"></i> Voir les détails';
      }

      // Créer ou mettre à jour le graphique
      createChart(data.chart_data);
    }

    // Afficher la section des résultats
    resultsSection.classList.remove("hidden");

    // Faire défiler jusqu'aux résultats
    resultsSection.scrollIntoView({
      behavior: "smooth",
    });
  }

  // Créer le graphique avec Chart.js
  function createChart(data) {
    const ctx = document.getElementById("results-chart").getContext("2d");

    // Détruire le graphique existant s'il y en a un
    if (chart) {
      chart.destroy();
    }

    // Préparer les couleurs
    const backgroundColors = data.labels.map((_, i) =>
      i === data.predicted_index ? "#4361ee" : "#e9ecef"
    );

    const borderColors = data.labels.map((_, i) =>
      i === data.predicted_index ? "#3a56d4" : "#dee2e6"
    );

    // Créer le nouveau graphique
    chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Probabilité (%)",
            data: data.values.map((v) => v * 100),
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: "Probabilité (%)",
            },
            ticks: {
              callback: function (value) {
                return value + "%";
              },
            },
            grid: {
              drawBorder: false,
            },
          },
          x: {
            title: {
              display: true,
              text: "Types de lésions",
            },
            grid: {
              display: false,
              drawBorder: false,
            },
          },
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return (
                  context.dataset.label +
                  ": " +
                  context.parsed.y.toFixed(1) +
                  "%"
                );
              },
            },
          },
        },
      },
    });
  }

  // Bouton pour lancer une nouvelle analyse
  newAnalysisBtn.addEventListener("click", function () {
    resetUpload();
    resultsSection.classList.add("hidden");
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // Bouton pour voir les détails
  const viewDetailsBtn = document.getElementById("view-details-btn");
  if (viewDetailsBtn) {
    viewDetailsBtn.addEventListener("click", function () {
      // Rediriger vers la page de résultats détaillés
      window.location.href = "/result";
    });
  }
});
