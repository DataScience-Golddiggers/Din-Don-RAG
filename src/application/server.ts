import express from 'express';
import path from 'path';
import bodyParser from 'body-parser';
import axios from 'axios';

const app = express();
const PORT = 3000;
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
// Use process.cwd() to find views and public relative to the project root, regardless of where the script is run from
app.set('views', path.join(process.cwd(), 'views'));
app.use(express.static(path.join(process.cwd(), 'public')));

// Bootstrap static files
app.use('/css', express.static(path.join(process.cwd(), 'node_modules/bootstrap/dist/css')));
app.use('/js', express.static(path.join(process.cwd(), 'node_modules/bootstrap/dist/js')));

// Global Lock
let isProcessing = false;

// Routes
app.get('/', (req, res) => {
    res.render('home', { title: 'Home' });
});

app.get('/chat', (req, res) => {
    res.render('chat', { title: 'Chat' });
});

app.get('/about', (req, res) => {
    res.render('about', { title: 'About Us' });
});

app.post('/api/ask', async (req, res) => {
    if (isProcessing) {
        return res.status(429).json({ error: 'System is busy. Please try again later.' });
    }

    const { question } = req.body;
    if (!question) {
        return res.status(400).json({ error: 'Question is required' });
    }

    isProcessing = true;

    try {
        const response = await axios.post(`${AI_SERVICE_URL}/ask`, { question });
        res.json(response.data);
    } catch (error: any) {
        console.error('Error calling AI Service:', error.message);
        res.status(500).json({ error: 'Failed to get answer from AI service.' });
    } finally {
        isProcessing = false;
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
