const path = require('path');

module.exports = {
    entry: {
        app: './src/app.js', // Single entry point instead of 6
    },
    output: {
        filename: '[name].bundle.js', // Will create app.bundle.js
        path: path.resolve(__dirname, 'public/js'),
        clean: true, // Clean output directory before build
    },
    mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
    devServer: {
        static: {
            directory: path.join(__dirname, 'public'),
        },
        port: 3000,
        hot: true,
        open: true,
        historyApiFallback: true, // Support for SPA routing
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                    },
                },
            },
            // Handle images
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
    optimization: {
        // Split chunks for better caching
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all',
                },
            },
        },
    },
    // Source maps for development
    devtool: process.env.NODE_ENV === 'production' ? false : 'eval-source-map',
};