pipeline {
    agent any
    stages{
        stage('running kivy_env'){
            sh 'kivy_env\Scripts\activate'
        }
        stage('new'){
            bat 'python main.py'
        }
    }
}