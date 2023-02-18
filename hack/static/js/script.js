function go_back(){
    window.history.back();
}

let menu = document.getElementById('menu');
let navbar = document.getElementById('navbar');
let cross = document.getElementById('cross');
let filebtn = document.getElementById('filebtn');
let file = document.getElementById('file');

menu.addEventListener('click', function(){
    if (navbar.classList.contains('hidden')){
        navbar.classList.remove('hidden');
        cross.classList.remove('hidden');
        menu.classList.add('hidden');
    }
});

cross.addEventListener('click', function(){
    if (!navbar.classList.contains('hidden')){
        cross.classList.add('hidden');
        navbar.classList.add('hidden');
        menu.classList.remove('hidden');
    }
});

filebtn.addEventListener('click', function(){
    if (file.classList.contains('hidden')){
        file.classList.remove('hidden');
    }
    else if (!file.classList.contains('hidden')){
        file.classList.add('hidden');
    }
});