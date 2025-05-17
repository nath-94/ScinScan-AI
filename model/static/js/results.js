document.addEventListener('DOMContentLoaded', function() {
    const resultContainer = document.getElementById('result-container');
    const urlParams = new URLSearchParams(window.location.search);
    const resultData = JSON.parse(localStorage.getItem('skinScanResult'));
    
    if (resultData && resultData.success) {
        displayResults(resultData);
    } else {
        displayError();
    }
    
    function displayResults(data) {
        // Créer la structure HTML des résultats
        const resultsHTML = `
            <div class="results-wrapper">
                <div class="results-image">
                    <img src="${data.file_url}" alt="Lésion analysée">
                </div>
                
                <div class="results-info">
                    <div class="result-card">
                        <div class="result-header">
                            <h3><i class="fas fa-clipboard-check"></i> Diagnostic préliminaire</h3>
                        </div>
                        <div class="result-body">
                            <div class="result-primary">
                                <h4>${data.class_full_name} (${data.class_name})</h4>
                                <p>${data.class_description}</p>
                            </div>
                            
                            <div class="result-details">
                                <div class="result-item">
                                    <div class="result-label">Niveau de risque:</div>
                                    <div class="result-value">
                                        <span class="badge ${getRiskBadgeClass(data.class_risk)}">${data.class_risk}</span>
                                    </div>
                                </div>
                                <div class="result-item">
                                    <div class="result-label">Confiance:</div>
                                    <div class="result-value">${(data.confidence * 100).toFixed(1)}%</div>
                                </div>
                            </div>
                            
                            <div class="result-recommendation">
                                <i class="fas fa-info-circle"></i> ${data.recommendation}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="results-chart">
                    <h3><i class="fas fa-chart-bar"></i> Probabilités par type de lésion</h3>
                    <div class="chart-container">
                        <canvas id="results-chart"></canvas>
                    </div>
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
                
                <div class="results-disclaimer">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p><strong>Note importante:</strong> Ce résultat est fourni à titre informatif uniquement et ne constitue pas un diagnostic médical. 
                       Consultez un dermatologue pour une évaluation professionnelle.</p>
                </div>
            </div>
        `;
        
        // Insérer le HTML dans le conteneur
        resultContainer.innerHTML = resultsHTML;
        
        // Créer le graphique avec Chart.js
        createChart(data.chart_data);
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
    
    function getRiskBadgeClass(risk) {
        if (risk.includes('Très faible') || risk.includes('Faible')) {
            return 'badge-success';
        } else if (risk.includes('Modéré')) {
            return 'badge-warning';
        } else {
            return 'badge-danger';
        }
    }
    
    function generateTableRows(data) {
        const labels = data.chart_data.labels;
        const values = data.chart_data.values;
        const predictedIndex = data.chart_data.predicted_index;
        
        // Définir les noms complets pour chaque classe
        const fullNames = {
            'akiec': 'Kératose actinique / Carcinome intraépidermique',
            'bcc': 'Carcinome basocellulaire',
            'bkl': 'Kératose bénigne',
            'df': 'Dermatofibrome',
            'nv': 'Naevus mélanocytaire',
            'vasc': 'Lésion vasculaire',
            'mel': 'Mélanome'
        };
        
        let rows = '';
        for (let i = 0; i < labels.length; i++) {
            const isHighlighted = (i === predictedIndex) ? 'highlighted-row' : '';
            const probability = (values[i] * 100).toFixed(1);
            
            rows += `
                <tr class="${isHighlighted}">
                    <td><strong>${labels[i]}</strong></td>
                    <td>${fullNames[labels[i]]}</td>
                    <td>${probability}%</td>
                    <td>
                        <div class="progress-bar-container">
                            <div class="progress-bar ${i === predictedIndex ? 'progress-primary' : 'progress-secondary'}" 
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
        const ctx = document.getElementById('results-chart');
        if (!ctx) return;
        
        // Préparer les couleurs
        const backgroundColors = data.labels.map((_, i) => 
            i === data.predicted_index ? '#4361ee' : '#e9ecef'
        );
        
        const borderColors = data.labels.map((_, i) => 
            i === data.predicted_index ? '#3a56d4' : '#dee2e6'
        );
        
        // Créer le graphique
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Probabilité (%)',
                    data: data.values.map(v => v * 100),
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
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
                            text: 'Probabilité (%)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            drawBorder: false
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Types de lésions'
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    });