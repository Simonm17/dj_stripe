const navSlide = () => {
    const burger = document.querySelector('.burger');
    const userDiv = document.querySelector('nav');
    const navLink = document.querySelectorAll('nav li');

    // Toggler
    burger.addEventListener('click', () => {
        userDiv.classList.toggle('nav-active');

        //Animate
        navLink.forEach((link, index) => {
            console.log(`${link}, ${index}`)
            if (link.style.animation) {
                link.style.animation = '';
            } else {
                link.style.animation = `userLinkFade 0.5s ease forwards`;
            }
        });
    });

}

const app = () => {
    navSlide();
}
app();