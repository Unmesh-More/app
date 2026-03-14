pipeline {
    agent any
    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Unmesh-More/app.git'
            }
        }
        stage('Run Kivy App') {
            steps {
                bat 'kivy_env\\Scripts\\python main.py'
            }
        }
    }
}