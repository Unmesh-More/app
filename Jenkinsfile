pipeline {
    agent any
    stages{
        stage('cloning'){
            step {
                git branch: 'main',
                url: 'https://github.com/Unmesh-More/app.git'
            } 
        }
        stage('running kivy_env'){
            step {
                sh 'kivy_env\Scripts\activate'
            }
        }
        stage('new'){
            step{
                bat 'python main.py'
            }
        }
    }
}