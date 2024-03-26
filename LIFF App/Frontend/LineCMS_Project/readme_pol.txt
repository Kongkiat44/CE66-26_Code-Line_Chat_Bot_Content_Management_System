create vue project:
    npm create vue@latest

then this project will be set to:
    √ Project name: ... LineCMS_Project
    √ Package name: ... linecms-project
    √ Add TypeScript? ... No / Yes
    √ Add JSX Support? ... No / Yes
    √ Add Vue Router for Single Page Application development? ... No / Yes
    √ Add Pinia for state management? ... No / Yes
    √ Add Vitest for Unit Testing? ... No / Yes
    √ Add an End-to-End Testing Solution? » No


to run dev: // now in .\LineCMS_Project

    // everytime to run and install module go to .\LineCMS_Project\LineCMS_Project
    cd LineCMS_Project 

    // now in .\LineCMS_Project\LineCMS_Project
    // install npm and their modules (the below command) only first time.
    npm install
    npm install axios
    npm install vuex
    npm install -g @vue/cli
    npm install --save-dev @types/vuex

    // to run development (in .\LineCMS_Project\LineCMS_Project)
    npm run dev

web start at Local:   http://127.0.0.1:5173/

// to build in docker go to .\LineCMS_Project
    docker build -t liff_linecms .



