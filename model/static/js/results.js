// @ts-nocheck
document.addEventListener("DOMContentLoaded", function () {
  const resultContainer = document.getElementById("result-container");
  const urlParams = new URLSearchParams(window.location.search);
  const resultData = JSON.parse(localStorage.getItem("skinScanResult"));

  if (resultData && resultData.success) {
    displayResults(resultData);
  } else {
    displayError();
  }

  function displayResults(data) {
    // Créer la structure HTML des résultats
    let resultsHTML = `
            <div class="results-wrapper">
                <div class="results-image">
                    <div class="image-container">
                        <img src="${data.annotated_image || data.file_url}" 
                          alt="Lésion analysée avec annotations"
                          onerror="this.onerror=null; if (this.src === '${
                            data.annotated_image
                          }') { this.src='${
      data.file_url
    }'; console.log('Fallback vers file_url:', '${data.file_url}'); }">
                        ${
                          data.annotated_image && data.total_moles_detected > 1
                            ? `<div class="image-badge">${data.total_moles_detected} détections</div>`
                            : ""
                        }
                    </div>
                    ${
                      data.annotated_image
                        ? '<p class="image-note"><i class="fas fa-info-circle"></i> Les grains de beauté détectés sont numérotés sur l\'image</p>'
                        : ""
                    }
                </div>
                
                <div class="results-info">
                    <div class="result-card">
                        <div class="result-header">
                            <h3><i class="fas fa-clipboard-check"></i> Diagnostic préliminaire - Résultat global</h3>
                        </div>
                        <div class="result-body">
                            <div class="result-primary">
                                <h4>${data.class_full_name} (${
      data.class_name
    })</h4>
                                <p>${data.class_description}</p>
                            </div>
                            
                            <div class="result-details">
                                <div class="result-item">
                                    <div class="result-label">Niveau de risque:</div>
                                    <div class="result-value">
                                        <span class="badge ${getRiskBadgeClass(
                                          data.class_risk
                                        )}">${data.class_risk}</span>
                                    </div>
                                </div>
                                <div class="result-item">
                                    <div class="result-label">Confiance:</div>
                                    <div class="result-value">${(
                                      data.confidence * 100
                                    ).toFixed(1)}%</div>
                                </div>
                                <div class="result-item">
                                    <div class="result-label">Grains de beauté détectés:</div>
                                    <div class="result-value">${
                                      data.total_moles_detected || 1
                                    }</div>
                                </div>
                                <div class="result-item">
                                    <div class="result-label">Grains de beauté analysés:</div>
                                    <div class="result-value">${
                                      data.analyzed_moles || 1
                                    }</div>
                                </div>
                            </div>
                            
                            <div class="result-recommendation">
                                <i class="fas fa-info-circle"></i> ${
                                  data.recommendation
                                }
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="results-chart">
                    <h3><i class="fas fa-chart-bar"></i> Probabilités par type de lésion</h3>

                    
                    ${generateMoleCharts(data)}
                </div>
                
                <div class="results-table">
                    <h3><i class="fas fa-table"></i> Détails des prédictions</h3>
                    <div class="table-responsive">
                        <table class="results-table-data">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Nom complet</th>
                                    <th>Probabilité</th>
                                    <th>Visualisation</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${generateTableRows(data)}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                ${generateMoleDetectionSection(data)}
                
                <div class="results-disclaimer">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p><strong>Note importante:</strong> Ce résultat est fourni à titre informatif uniquement et ne constitue pas un diagnostic médical. 
                       Consultez un dermatologue pour une évaluation professionnelle.</p>
                </div>
            </div>
        `;

    // Insérer le HTML dans le conteneur
    resultContainer.innerHTML = resultsHTML;

    // Créer le graphique principal avec Chart.js
    createChart(data.chart_data);

    // Créer les graphiques pour chaque grain de beauté détecté
    if (data.all_detections && data.all_detections.length > 1) {
      data.all_detections.forEach((mole, index) => {
        if (mole.chart_data) {
          createMoleChart(mole.chart_data, `mole-chart-${index}`);
        }
      });
    }
  }

  function displayError() {
    resultContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Aucun résultat disponible</h3>
                <p>Les résultats ne sont pas disponibles ou ont expiré.</p>
                <a href="/" class="btn btn-primary"><i class="fas fa-home"></i> Retour à l'accueil</a>
            </div>
        `;
  }

  function generateMoleCharts(data) {
    // Vérifier si nous avons des détections multiples
    if (!data.all_detections || data.all_detections.length <= 1) {
      return ""; // Retourner une chaîne vide si aucune détection multiple
    }

    let chartsHTML = "";

    // Générer un conteneur de graphique pour chaque grain de beauté détecté
    data.all_detections.forEach((mole, index) => {
      if (mole.chart_data) {
        // Ajouter un en-tête et un graphique pour chaque grain de beauté
        chartsHTML += `
          <div class="mole-chart-section">
            <h4 class="mole-chart-title">
              <div class="mole-number-indicator">${index + 1}</div> 
              Grain de beauté #${index + 1} - ${mole.class_full_name} (${
          mole.class_name
        })
            </h4>
            <div class="chart-container">
              <canvas id="mole-chart-${index}"></canvas>
            </div>
          </div>
        `;
      }
    });

    return chartsHTML;
  }

  function generateMoleDetectionSection(data) {
    // Vérifier si nous avons des détections multiples
    if (!data.all_detections || data.all_detections.length <= 1) {
      return ""; // Retourner une chaîne vide si aucune détection multiple
    }

    let molesHTML = "";

    // Générer le HTML pour chaque grain de beauté détecté
    data.all_detections.forEach((mole, index) => {
      const isHighRisk =
        mole.class_risk === data.class_risk &&
        mole.class_name === data.class_name;
      const borderClass = isHighRisk ? "mole-card-highlight" : "";

      // Calculer la classe de badge pour le niveau de risque
      const riskBadgeClass = getRiskBadgeClass(mole.class_risk);

      // Identifiant unique pour le graphique de ce grain de beauté
      const chartId = `mole-chart-${index}`;

      molesHTML += `
            <div class="mole-card ${borderClass}">
                <div class="mole-header">
                    <div class="mole-number">${index + 1}</div>
                    <h4>Grain de beauté #${index + 1} ${
        isHighRisk
          ? '<span class="highest-risk-label">Risque le plus élevé</span>'
          : ""
      }</h4>
                </div>
                <div class="mole-body">
                    <div class="mole-info">
                        <div class="mole-type">
                            <strong>${mole.class_full_name}</strong> (${
        mole.class_name
      })
                        </div>
                        <div class="mole-risk">
                            Risque: <span class="badge ${riskBadgeClass}">${
        mole.class_risk
      }</span>
                        </div>
                        <div class="mole-confidence">
                            Confiance: ${(mole.confidence * 100).toFixed(1)}%
                        </div>
                        <div class="mole-description">
                            ${
                              mole.class_description
                                ? `<details>
                                <summary>Description</summary>
                                <p>${mole.class_description}</p>
                              </details>`
                                : ""
                            }
                        </div>
                    </div>
                </div>
            </div>
            `;
    });

    return `
        <div class="moles-detection-section">
            <h3><i class="fas fa-search"></i> Détail des grains de beauté détectés (${data.all_detections.length})</h3>
            <p class="moles-detection-help">Les numéros correspondent aux grains de beauté identifiés sur l'image.</p>
            <div class="moles-grid">
                ${molesHTML}
            </div>
            <div class="moles-info-note">
                <i class="fas fa-info-circle"></i>
                <p>Le grain de beauté au risque le plus élevé est mis en évidence avec une bordure rouge. Chaque grain de beauté dispose de son propre graphique de probabilités.</p>
            </div>
        </div>
        `;
  }

  function getRiskBadgeClass(risk) {
    if (risk.includes("Très faible") || risk.includes("Faible")) {
      return "badge-success";
    } else if (risk.includes("Modéré")) {
      return "badge-warning";
    } else {
      return "badge-danger";
    }
  }

  function generateTableRows(data) {
    const labels = data.chart_data.labels;
    const values = data.chart_data.values;
    const predictedIndex = data.chart_data.predicted_index;

    // Définir les noms complets pour chaque classe
    const fullNames = {
      akiec: "Kératose actinique / Carcinome intraépidermique",
      bcc: "Carcinome basocellulaire",
      bkl: "Kératose bénigne",
      df: "Dermatofibrome",
      nv: "Naevus mélanocytaire",
      vasc: "Lésion vasculaire",
      mel: "Mélanome",
    };

    let rows = "";
    for (let i = 0; i < labels.length; i++) {
      const isHighlighted = i === predictedIndex ? "highlighted-row" : "";
      const probability = (values[i] * 100).toFixed(1);

      rows += `
                <tr class="${isHighlighted}">
                    <td><strong>${labels[i]}</strong></td>
                    <td>${fullNames[labels[i]]}</td>
                    <td>${probability}%</td>
                    <td>
                        <div class="progress-bar-container">
                            <div class="progress-bar ${
                              i === predictedIndex
                                ? "progress-primary"
                                : "progress-secondary"
                            }" 
                                style="width: ${probability}%">
                            </div>
                        </div>
                    </td>
                </tr>
            `;
    }

    return rows;
  }

  function createChart(data) {
    const ctx = document.getElementById("results-chart");
    if (!ctx) return;

    // Préparer les couleurs
    const backgroundColors = data.labels.map((_, i) =>
      i === data.predicted_index ? "#4361ee" : "#e9ecef"
    );

    const borderColors = data.labels.map((_, i) =>
      i === data.predicted_index ? "#3a56d4" : "#dee2e6"
    );

    // Créer le graphique
    const chart = new Chart(ctx, {
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

  // Fonction pour créer un graphique pour un grain de beauté spécifique
  function createMoleChart(data, chartId) {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;

    // Préparer les couleurs
    const backgroundColors = data.labels.map((_, i) =>
      i === data.predicted_index ? "#4361ee" : "#e9ecef"
    );

    const borderColors = data.labels.map((_, i) =>
      i === data.predicted_index ? "#3a56d4" : "#dee2e6"
    );

    // Créer le graphique
    const chart = new Chart(ctx, {
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
});
