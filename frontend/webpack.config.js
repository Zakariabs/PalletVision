const { all } = require('axios');
const path = require('path');

module.exports = {
    entry: {
        index: './src/index.js', // Entry file for the main index page
        managerDashboard: './src/managerDashboard.js', // Entry for the Manager Dashboard
        stationDashboard: './src/stationDashboard.js', // Entry for the Station Dashboard
        efficiencyDashboard: './src/efficiencyDashboard.js', // Entry for the Station Dashboard
        login: './src/login.js'
        allRequests: './src/all_Requests.js', // Entry for the All Requests page
        log_page: './src/logs.js', // Entry for the Log page
    },
    output: {
        filename: '[name].bundle.js', // Output filename pattern: index.bundle.js, managerDashboard.bundle.js, etc.
        path: path.resolve(__dirname, 'public/js'), // Output directory for JS files
    },
    devServer: {
        static: {
            directory: path.join(__dirname, 'public'), // Serve static files from the public directory
        },
        port: 3000, // Port for the development server
        hot: true, // Enable Hot Module Replacement
        open: true, // Automatically open the browser
    },
    module: {
        rules: [
            {
                test: /\.css$/, // Process CSS files
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.js$/, // Transpile JavaScript files
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'], // Support for modern JavaScript
                    },
                },
            },
        ],
    },
    mode: 'development', // Set to 'development' or 'production' based on your environment
};
