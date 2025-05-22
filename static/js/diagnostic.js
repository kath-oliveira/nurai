// JavaScript para o formulário de diagnóstico financeiro
document.addEventListener('DOMContentLoaded', function() {
    // Mostrar/ocultar campo de estratégia de propriedade intelectual
    const propriedadeSim = document.getElementById('propriedade_sim');
    const propriedadeNao = document.getElementById('propriedade_nao');
    const estrategiaDiv = document.getElementById('estrategia_propriedade_div');
    
    if (propriedadeSim && propriedadeNao && estrategiaDiv) {
        propriedadeSim.addEventListener('change', function() {
            if (this.checked) {
                estrategiaDiv.style.display = 'block';
            }
        });
        
        propriedadeNao.addEventListener('change', function() {
            if (this.checked) {
                estrategiaDiv.style.display = 'none';
            }
        });
    }
    
    // Validação do formulário
    const form = document.getElementById('diagnosticForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            const activeSection = document.querySelector('.form-section.active');
            const requiredFields = activeSection.querySelectorAll('[required]');
            
            let isValid = true;
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                alert('Por favor, preencha todos os campos obrigatórios.');
            }
        });
    }
    
    // Formatação de campos monetários
    const monetaryInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    if (monetaryInputs) {
        monetaryInputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (this.value) {
                    // Formatar para duas casas decimais
                    this.value = parseFloat(this.value).toFixed(2);
                }
            });
        });
    }
});
