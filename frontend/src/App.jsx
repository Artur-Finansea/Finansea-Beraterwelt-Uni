
import { useEffect, useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {

    // Status unseres Flask-Backends
    const [backendStatus, setBackendStatus] = useState(
        'Verbindung wird hergestellt...'
    )

    // Daten von Flask abrufen
    useEffect(() => {
        fetch('/api/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Serverfehler')
                }
                return response.json()
            })
            .then(data => {
                setBackendStatus(data.status)
            })
            .catch(error => {
                console.error(error)
                setBackendStatus('Backend nicht erreichbar')
            })
    }, [])

    return (
        <div className="min-vh-100 bg-light">

            {/* Navigation */}
            <header>
                <nav className="navbar navbar-dark bg-dark px-4" aria-label="Hauptnavigation">
                    <span className="navbar-brand mb-0 h1">
                        Finansea | Beraterwelt
                    </span>
                </nav>
            </header>

            {/* Dashboard */}
            <main className="container py-5">

                <h1>Berater-Dashboard</h1>

                <p className="text-muted">
                    Willkommen in der Finansea-Beraterwelt!
                </p>

                {/* Verbindung zum Backend */}
                <div className="alert alert-info mt-4" role="status" aria-live="polite">
                    <strong>Backend-Status: </strong>
                    {backendStatus}
                </div>

                {/* Dashboard-Karten */}
                <section className="row g-3 mt-4" aria-label="Dashboard-Kennzahlen">

                    <div className="col-md-4">
                        <article className="card shadow-sm h-100">
                            <div className="card-body">
                                <h2 className="h5 card-title">Kunden</h2>
                                <p className="h2">0</p>
                                <p className="text-muted">
                                    Aktive Kunden
                                </p>
                            </div>
                        </article>
                    </div>

                    <div className="col-md-4">
                        <article className="card shadow-sm h-100">
                            <div className="card-body">
                                <h2 className="h5 card-title">Beratungen</h2>
                                <p className="h2">0</p>
                                <p className="text-muted">
                                    Beratungsgespräche
                                </p>
                            </div>
                        </article>
                    </div>

                    <div className="col-md-4">
                        <article className="card shadow-sm h-100">
                            <div className="card-body">
                                <h2 className="h5 card-title">Aufgaben</h2>
                                <p className="h2">0</p>
                                <p className="text-muted">
                                    Offene Aufgaben
                                </p>
                            </div>
                        </article>
                    </div>

                </section>
            </main>
        </div>
    )
}

export default App
