from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import os
import random
import pathlib
from datetime import datetime

from simulation import VitalSignGenerator, ThreatIntelligence
from ml_model import AnomalyDetector
from federated import FederatedSimulator

app = FastAPI(title="Cybher - Healthcare Security Platform")

# Mount static files
static_dir = pathlib.Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
generator = VitalSignGenerator()
detector = AnomalyDetector()
federated_sim = FederatedSimulator()
threat_intel = ThreatIntelligence()

# Session statistics
session_stats = {
    "start_time": datetime.now().isoformat(),
    "total_requests": 0,
    "anomalies_detected": 0,
    "model_accuracy": 0.0,
    "last_retrain": None
}

# Train Anomaly Detector on startup with normal data
print("--> Training initial Anomaly Detector on Normal Data...")
initial_data = [generator.generate_packet() for _ in range(500)]
detector.train(initial_data)

# Validation Step matching Objective 2
print("--> Validating Model against Mixed Data (Normal + Attacks)...")
test_data = []
test_labels = []

# 50 Normal
for _ in range(50):
    test_data.append(generator.generate_packet())
    test_labels.append(False)

# 50 Attacks (Mixed types)
attack_types = ['spike', 'flatline', 'spoof', 'noise', 'replay', 'mitm']
for _ in range(50):
    p = generator.generate_packet(anomaly_type=random.choice(attack_types))
    test_data.append(p)
    test_labels.append(True)

correct = 0
for i, p in enumerate(test_data):
    pred = detector.predict(p)
    if pred == test_labels[i]:
        correct += 1

session_stats["model_accuracy"] = (correct / 100) * 100
print(f"--> Model Validation Complete. Accuracy on Mixed Stream: {session_stats['model_accuracy']}%")
print("--> Ready to detect threats.")


@app.get("/")
async def read_root():
    """Serve the main dashboard"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
        with open(file_path, "r", encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), media_type="text/html")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load index.html: {str(e)}"}
        )


@app.get("/stream")
async def stream_data():
    """Returns a single data packet with anomaly prediction."""
    try:
        session_stats["total_requests"] += 1
        
        # Randomly decide to inject anomaly (10% chance)
        anomaly_type = None
        if random.random() < 0.1:
            anomaly_type = random.choice(['spike', 'flatline', 'spoof', 'noise'])
            
        packet = generator.generate_packet(anomaly_type=anomaly_type)
        
        # Run anomaly detection
        try:
            is_detected = detector.predict(packet)
        except Exception as e:
            print(f"Detection error: {e}")
            is_detected = False
        
        packet['anomaly_detected'] = bool(is_detected)
        
        # Log to threat intelligence
        if packet['is_anomaly_injected'] or is_detected:
            threat_intel.log_threat(
                packet['attack_type'], 
                detected=is_detected,
                blocked=is_detected
            )
            if is_detected:
                session_stats["anomalies_detected"] += 1
        
        return JSONResponse(content=packet)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Stream generation failed: {str(e)}"}
        )


@app.post("/inject-attack")
async def inject_attack(request: Request):
    """Manually inject an attack into the data stream"""
    try:
        data = await request.json()
        attack_type = data.get("type", "spike")
        duration = data.get("duration", 10)
        
        # Validate attack type
        valid_types = ['spike', 'flatline', 'spoof', 'noise', 'replay', 'mitm']
        if attack_type not in valid_types:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid attack type. Must be one of: {valid_types}"}
            )
        
        # Validate duration
        duration = max(1, min(int(duration), 100))  # Between 1 and 100
        
        generator.set_attack(attack_type, duration)
        threat_intel.log_threat(attack_type, detected=False, blocked=False)
        return JSONResponse(content={
            "status": "success", 
            "message": f"{attack_type} injection active for {duration} packets",
            "attack_type": attack_type
        })
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to inject attack: {str(e)}"}
        )


@app.post("/clear-attack")
async def clear_attack():
    """Clear any active attack"""
    generator.clear_attack()
    return JSONResponse(content={"status": "success", "message": "Attack cleared"})


@app.get("/system-stats")
async def system_stats():
    """Get system resource statistics"""
    return JSONResponse(content={
        "cpu": random.randint(20, 45),
        "memory": random.randint(40, 65),
        "network_load": random.randint(10, 80),
        "active_connections": random.randint(1, 10),
        "uptime_seconds": (datetime.now() - datetime.fromisoformat(session_stats["start_time"])).seconds
    })


def make_json_serializable(obj):
    """Convert object to JSON-serializable format"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    else:
        return str(obj)

@app.get("/session-stats")
async def get_session_stats():
    """Get session statistics"""
    stats = generator.get_statistics()
    threat_summary = threat_intel.get_summary()
    
    # Combine all stats
    combined = {
        **session_stats,
        **stats,
        "threat_summary": threat_summary
    }
    
    # Ensure all values are JSON serializable
    serializable_data = make_json_serializable(combined)
    return JSONResponse(content=serializable_data)


@app.get("/threat-intel")
async def get_threat_intel():
    """Get threat intelligence summary"""
    summary = threat_intel.get_summary()
    serializable_data = make_json_serializable(summary)
    return JSONResponse(content=serializable_data)


@app.get("/patients")
async def get_patients():
    """Get all patient profiles"""
    return JSONResponse(content=generator.get_patients())


@app.post("/patients/switch")
async def switch_patient(request: Request):
    """Switch to a different patient"""
    data = await request.json()
    patient_id = data.get("patient_id")
    success = generator.set_patient(patient_id)
    if success:
        return JSONResponse(content={
            "status": "success",
            "current_patient": generator.get_current_patient()
        })
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": "Patient not found"}
    )


@app.get("/patients/current")
async def get_current_patient():
    """Get current patient info"""
    return JSONResponse(content=generator.get_current_patient())


@app.post("/model/retrain")
async def retrain_model():
    """Retrain the anomaly detection model"""
    print("--> Retraining Anomaly Detector...")
    
    # Generate fresh training data
    training_data = [generator.generate_packet() for _ in range(500)]
    detector.train(training_data)
    
    # Validate
    test_data = []
    test_labels = []
    
    for _ in range(50):
        test_data.append(generator.generate_packet())
        test_labels.append(False)
    
    for _ in range(50):
        p = generator.generate_packet(anomaly_type=random.choice(['spike', 'flatline', 'spoof', 'noise']))
        test_data.append(p)
        test_labels.append(True)
    
    correct = sum(1 for i, p in enumerate(test_data) if detector.predict(p) == test_labels[i])
    accuracy = (correct / 100) * 100
    
    session_stats["model_accuracy"] = accuracy
    session_stats["last_retrain"] = datetime.now().isoformat()
    
    return JSONResponse(content={
        "status": "success",
        "message": "Model retrained successfully",
        "new_accuracy": accuracy
    })


@app.get("/model/status")
async def model_status():
    """Get model status and accuracy"""
    return JSONResponse(content={
        "is_trained": detector.is_trained,
        "accuracy": session_stats["model_accuracy"],
        "last_retrain": session_stats["last_retrain"],
        "contamination": 0.1,
        "n_estimators": 100
    })


@app.post("/train-fl")
async def train_fl(request: Request):
    """Run federated learning simulation"""
    rounds = 5
    try:
        data = await request.json()
        rounds = data.get("rounds", 5)
        # Validate rounds
        rounds = max(1, min(rounds, 20))  # Between 1 and 20
    except:
        rounds = 5
    
    try:
        results = federated_sim.run_simulation(rounds=rounds)
        serializable_results = make_json_serializable(results)
        return JSONResponse(content=serializable_results)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Federated learning simulation failed: {str(e)}"}
        )


@app.get("/attack-types")
async def get_attack_types():
    """Get available attack types with descriptions"""
    return JSONResponse(content={
        "attacks": [
            {
                "id": "spike",
                "name": "Sensor Spike",
                "description": "Sudden high-value spikes simulating voltage surges or sensor manipulation",
                "severity": "high",
                "icon": "fa-bolt"
            },
            {
                "id": "flatline",
                "name": "Flatline DoS",
                "description": "Complete signal loss simulating denial of service or sensor failure",
                "severity": "critical",
                "icon": "fa-skull-crossbones"
            },
            {
                "id": "noise",
                "name": "Signal Noise",
                "description": "High-variance random noise degrading data integrity",
                "severity": "high",
                "icon": "fa-wave-square"
            },
            {
                "id": "spoof",
                "name": "Identity Spoof",
                "description": "Rigid low-variance data mimicking fake but plausible vitals",
                "severity": "medium",
                "icon": "fa-user-secret"
            },
            {
                "id": "replay",
                "name": "Replay Attack",
                "description": "Repeated identical values indicating captured data replay",
                "severity": "medium",
                "icon": "fa-rotate"
            },
            {
                "id": "mitm",
                "name": "Man-in-the-Middle",
                "description": "Subtly altered values suggesting data interception",
                "severity": "high",
                "icon": "fa-mask"
            }
        ]
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
