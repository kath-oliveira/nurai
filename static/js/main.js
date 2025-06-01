// JavaScript principal para o sistema CFO as a Service

// Função para inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializa popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Inicializa a funcionalidade de barra lateral colapsável
    initSidebar();

    // Inicializa gráficos se existirem no DOM
    initCharts();
});

// Função para inicializar a barra lateral colapsável
function initSidebar() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    // Se não existir barra lateral, não faz nada
    if (!sidebar) return;
    
    // Verifica se deve iniciar colapsado em dispositivos móveis
    if (window.innerWidth < 768) {
        sidebar.classList.add('collapsed');
        if (mainContent) mainContent.style.marginLeft = '0';
    }
    
    // Adiciona evento de clique no botão de toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Atualiza o ícone do botão
            const icon = this.querySelector('i');
            if (icon) {
                if (sidebar.classList.contains('collapsed')) {
                    icon.classList.remove('bi-chevron-left');
                    icon.classList.add('bi-chevron-right');
                } else {
                    icon.classList.remove('bi-chevron-right');
                    icon.classList.add('bi-chevron-left');
                }
            }
            
            // Ajusta a margem do conteúdo principal
            if (mainContent) {
                if (sidebar.classList.contains('collapsed')) {
                    mainContent.style.marginLeft = '0';
                } else {
                    mainContent.style.marginLeft = '250px';
                }
            }
        });
    }
}

// Função para inicializar gráficos
function initCharts() {
    // Gráfico de receitas e custos
    const revenueChartElement = document.getElementById('revenueChart');
    if (revenueChartElement) {
        // Obtém dados do elemento
        const chartData = JSON.parse(revenueChartElement.getAttribute('data-chart'));
        
        new Chart(revenueChartElement, {
            type: 'line',
            data: {
                labels: chartData.anos,
                datasets: [
                    {
                        label: 'Receitas',
                        data: chartData.receitas,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Custos',
                        data: chartData.custos,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('pt-BR', { 
                                        style: 'currency', 
                                        currency: 'BRL',
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 0
                                    }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return 'R$ ' + (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return 'R$ ' + (value / 1000).toFixed(0) + 'K';
                                } else {
                                    return 'R$ ' + value;
                                }
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Gráfico de estrutura de custos
    const costStructureElement = document.getElementById('costStructureChart');
    if (costStructureElement) {
        // Obtém dados do elemento
        const chartData = JSON.parse(costStructureElement.getAttribute('data-chart'));
        
        new Chart(costStructureElement, {
            type: 'doughnut',
            data: {
                labels: ['Custos Fixos', 'Custos Variáveis'],
                datasets: [{
                    data: [chartData.custos_fixos_pct, chartData.custos_variaveis_pct],
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.7)',
                        'rgba(220, 53, 69, 0.7)'
                    ],
                    borderColor: [
                        'rgba(13, 110, 253, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Gráfico de indicadores financeiros (radar)
    const indicatorsChartElement = document.getElementById('indicatorsChart');
    if (indicatorsChartElement) {
        // Obtém dados do elemento
        const chartData = JSON.parse(indicatorsChartElement.getAttribute('data-chart'));
        
        new Chart(indicatorsChartElement, {
            type: 'radar',
            data: {
                labels: ['Rentabilidade', 'Liquidez', 'Endividamento', 'Eficiência', 'Crescimento'],
                datasets: [{
                    label: 'Pontuação (0-10)',
                    data: chartData.scores,
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(13, 110, 253, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 10
                    }
                }
            }
        });
    }
}

// Função para formatar valores monetários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { 
        style: 'currency', 
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Função para validar formulários
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Função para confirmar ações importantes
function confirmAction(message) {
    return confirm(message || 'Tem certeza que deseja realizar esta ação?');
}
