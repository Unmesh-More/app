pipeline {
    agent any
    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Unmesh-More/app.git'
            }
        }
        stage('Check or Create Virtual Environment') {
            steps {
                bat '''
                IF EXIST kivy_env (
                    echo Virtual environment already exists
                ) ELSE (
                    echo Creating virtual environment
                    python -m venv kivy_env
                )
                '''
            }
        }
        stage('Install Dependencies') {
            steps {
                bat 'kivy_env\\Scripts\\pip install -r requirements.txt'
            }
        }
        stage('Run Kivy App') {
            steps {
                bat 'kivy_env\\Scripts\\python main.py'
            }
        }
    }
}