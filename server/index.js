const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
const { spawn } = require('child_process');

// Initialize express app
const app = express();
const PORT = process.env.PORT || 8001;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Set up storage for image uploads
const UPLOAD_FOLDER = path.join(__dirname, 'images');
if (!fs.existsSync(UPLOAD_FOLDER)) {
    fs.mkdirSync(UPLOAD_FOLDER);
}

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_FOLDER);
    },
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: (req, file, cb) => {
        const allowedExtensions = /png|jpg|jpeg/;
        const extname = allowedExtensions.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedExtensions.test(file.mimetype);

        if (extname && mimetype) {
            return cb(null, true);
        } else {
            cb('Error: Images Only!');
        }
    }
});

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

// Serve the index page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

// Handle image upload and prediction
app.post('/api/analyze', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePath = req.file.path;

    // Spawn a Python process to handle prediction
    const pythonProcess = spawn('python3', ['predict.py', filePath]);

    pythonProcess.stdout.on('data', (data) => {
        const result = JSON.parse(data.toString());
        res.json(result);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
        res.status(500).json({ error: 'Prediction failed' });
    });

    pythonProcess.on('close', () => {
        // Clean up the uploaded file
        fs.unlinkSync(filePath);
    });
});

// Fetch result data from CSV (similar to getDataFromCSV function)
app.get('/api/result', (req, res) => {
    const productId = parseInt(req.query.id, 10);

    if (isNaN(productId)) {
        return res.status(400).json({ error: 'Invalid product ID' });
    }

    // Load CSV and return the data for the given product ID
    const csvFilePath = path.join(__dirname, 'data_files', 'supplement_info.csv');
    const csv = fs.readFileSync(csvFilePath, 'utf8');
    const rows = csv.split('\n').slice(1);
    let result = null;

    rows.forEach((row) => {
        const columns = row.split(',');
        if (parseInt(columns[0], 10) === productId) {
            result = {
                disease_name: columns[1],
                supplement_name: columns[2],
                supplement_image: columns[3],
                buy_link: columns[4]
            };
        }
    });

    if (result) {
        res.json(result);
    } else {
        res.status(404).json({ error: 'Data not found' });
    }
});

// Fallback for React
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build/index.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
