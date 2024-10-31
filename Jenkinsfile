pipeline {
    agent any
    options {
        timeout(time: 1, unit: 'SECONDS')
    }
    stages{
        stage('Print') {
            steps {
                fileExists './PiMono/pimono.py'
            }
        }
    }
    
}