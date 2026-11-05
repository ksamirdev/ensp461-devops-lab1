pipeline {
    agent any
    options { disableConcurrentBuilds() }
    triggers { pollSCM('H/2 * * * *') }

    stages {
        stage('Build') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/pip install -q -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh '.venv/bin/python -m pytest -v --junitxml=test-results.xml'
            }
            post {
                always { junit 'test-results.xml' }
            }
        }
        stage('Package') {
            steps {
                sh 'mkdir -p dist && tar czf dist/text-stats-${BUILD_NUMBER}.tar.gz service requirements.txt'
                archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
            }
        }
        stage('Deploy') {
            steps {
                sh 'sudo /usr/local/bin/text-stats-deploy "$WORKSPACE/dist/text-stats-${BUILD_NUMBER}.tar.gz"'
            }
        }
    }

    post {
        success { echo "Build ${BUILD_NUMBER} deployed" }
        failure { echo "Build ${BUILD_NUMBER} failed, deployed release unchanged" }
    }
}
