// Script pour la navigation interactive
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner tous les liens de navigation
    const navLinks = document.querySelectorAll('.nav a');
    
    // 1. Gestion des liens d'ancrage (navigation dans la même page)
    const sections = {};
    let sectionsArray = [];
    
    // Récupérer toutes les sections correspondant aux liens d'ancrage
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Si c'est un lien d'ancrage (commence par #)
        if (href.startsWith('#')) {
            const section = document.querySelector(href);
            if (section) {
                sections[href] = section;
                sectionsArray.push(section);
            }
        }
    });
    
    // Fonction pour mettre à jour les classes actives en fonction du défilement
    function updateActiveSection() {
        // Obtenir la position de défilement actuelle
        const scrollPosition = window.scrollY + window.innerHeight / 3;
        
        // Parcourir toutes les sections
        for (const [href, section] of Object.entries(sections)) {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            // Vérifier si la position de défilement est dans cette section
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                // Enlever la classe active de tous les liens
                navLinks.forEach(link => link.classList.remove('active'));
                
                // Ajouter la classe active au lien correspondant
                document.querySelector(`.nav a[href="${href}"]`).classList.add('active');
            }
        }
        
        // Gestion spéciale pour "Accueil" - actif si au début de la page
        if (scrollPosition < (sectionsArray.length > 0 ? sectionsArray[0].offsetTop : Infinity)) {
            navLinks.forEach(link => link.classList.remove('active'));
            document.querySelector('.nav a[href="/"]').classList.add('active');
        }
    }
    
    // Mettre à jour les liens actifs au chargement de la page
    updateActiveSection();
    
    // Mettre à jour les liens actifs lors du défilement
    window.addEventListener('scroll', updateActiveSection);
    
    // 2. Gestion des clics sur les liens
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Si c'est un lien d'ancrage (navigation interne)
            if (href.startsWith('#')) {
                e.preventDefault();
                
                // Faire défiler en douceur vers la section
                const section = document.querySelector(href);
                if (section) {
                    window.scrollTo({
                        top: section.offsetTop,
                        behavior: 'smooth'
                    });
                }
                
                // Mettre à jour les classes actives
                navLinks.forEach(link => link.classList.remove('active'));
                this.classList.add('active');
            }
            // Si c'est un lien externe (comme /chatbot), laissez le comportement par défaut
        });
    });
    
    // 3. Marquer le lien "Assistant IA" comme actif sur la page du chatbot
    // Vérifier si nous sommes sur la page du chatbot
    if (window.location.pathname === '/chatbot') {
        navLinks.forEach(link => link.classList.remove('active'));
        document.querySelector('.nav a[href="/chatbot"]').classList.add('active');
    }
});