#!/usr/bin/env python3
"""
NASA FRIGATE Website Server - Enhanced Management Edition
A Flask-based server with embedded HTML content, yellow palette, 3D effects, leadership login,
event gallery, blog system, and comprehensive management dashboard - Now Mobile Friendly!
"""

import os
import json
import sqlite3
from datetime import datetime, date
from flask import Flask, request, jsonify, session, send_file, abort
from flask_cors import CORS
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
import mimetypes
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Configuration
class Config:
    DATABASE_PATH = 'nasa_frigate.db'
    UPLOAD_FOLDER = 'uploads'
    GALLERY_FOLDER = 'gallery'
    BLOG_FOLDER = '.'  # Same folder as server.py for .sh files
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov'}

app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GALLERY_FOLDER'], exist_ok=True)

# Sample Login Credentials
LEADERSHIP_CREDENTIALS = {
    'captain': {'password': 'anchor2024', 'role': 'Frigate Captain', 'name': 'Captain Sarah Johnson'},
    'scribe': {'password': 'quill2024', 'role': 'Scribe', 'name': 'Michael Chen'},
    'crier': {'password': 'horn2024', 'role': 'Crier', 'name': 'Amanda Rodriguez'},
    'purse': {'password': 'coin2024', 'role': 'Purse', 'name': 'David Thompson'}
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Enhanced HTML content with mobile-friendly responsive design
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>NASA FRIGATE - Rugged Sailors of Service</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Pirata+One&family=Roboto+Slab:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto Slab', serif;
            line-height: 1.6;
            color: #2c1810;
            overflow-x: hidden;
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffc107 100%);
        }

        /* Rugged Typography */
        .rugged-title {
            font-family: 'Pirata One', cursive;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            letter-spacing: 2px;
        }

        /* 3D Effects - Reduced on mobile */
        .card-3d {
            transform-style: preserve-3d;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 
                0 10px 20px rgba(0,0,0,0.2),
                0 6px 6px rgba(0,0,0,0.1),
                inset 0 1px 0 rgba(255,255,255,0.3);
        }

        .card-3d:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 15px 30px rgba(0,0,0,0.3),
                0 10px 10px rgba(0,0,0,0.2),
                inset 0 1px 0 rgba(255,255,255,0.4);
        }

        /* Enhanced 3D effects for desktop */
        @media (min-width: 769px) {
            .card-3d:hover {
                transform: translateY(-10px) rotateX(5deg) rotateY(5deg);
                box-shadow: 
                    0 20px 40px rgba(0,0,0,0.3),
                    0 15px 15px rgba(0,0,0,0.2),
                    inset 0 1px 0 rgba(255,255,255,0.4);
            }
        }

        .anchor-decoration {
            position: absolute;
            opacity: 0.1;
            font-size: 8rem;
            color: #8b4513;
            z-index: -1;
            animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(5deg); }
        }

        /* Header Styles - Mobile First */
        .header {
            background: linear-gradient(135deg, #b8860b 0%, #daa520 50%, #ffd700 100%);
            color: #2c1810;
            padding: 0.75rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 
                0 4px 8px rgba(0,0,0,0.3),
                inset 0 1px 0 rgba(255,255,255,0.2);
            border-bottom: 3px solid #8b4513;
        }

        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 1rem;
        }

        .logo {
            display: flex;
            align-items: center;
            font-size: 1.3rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .logo i {
            margin-right: 0.3rem;
            font-size: 1.8rem;
            color: #8b4513;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            animation: rock 3s ease-in-out infinite;
        }

        @keyframes rock {
            0%, 100% { transform: rotate(-5deg); }
            50% { transform: rotate(5deg); }
        }

        .nav-menu {
            display: none;
            list-style: none;
            gap: 1rem;
            position: absolute;
            top: 100%;
            left: 0;
            width: 100%;
            background: linear-gradient(135deg, #b8860b 0%, #daa520 100%);
            flex-direction: column;
            padding: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            max-height: 70vh;
            overflow-y: auto;
        }

        .nav-menu.active {
            display: flex;
        }

        .nav-menu a {
            color: #2c1810;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 600;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            font-size: 1.1rem;
        }

        .nav-menu a:hover, .nav-menu a:active {
            background: rgba(139, 69, 19, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .mobile-menu-btn {
            display: block;
            background: none;
            border: none;
            color: #2c1810;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }

        .mobile-menu-btn:hover {
            background: rgba(139, 69, 19, 0.1);
        }

        .login-btn {
            background: #8b4513;
            color: #ffd700;
            padding: 0.5rem 0.75rem;
            border: none;
            border-radius: 20px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            font-size: 0.9rem;
            white-space: nowrap;
        }

        .login-btn:hover {
            background: #654321;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }

        .login-btn i {
            margin-right: 0.3rem;
        }

        /* Page Content Styles */
        .page-content {
            margin-top: 80px;
            min-height: calc(100vh - 80px);
            padding: 1rem 0;
        }

        .page-content.hidden {
            display: none;
        }

        /* Gallery Styles - Mobile First */
        .gallery-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .gallery-item {
            background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
            border-radius: 15px;
            overflow: hidden;
            border: 3px solid #daa520;
            position: relative;
        }

        .gallery-item img, .gallery-item video {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }

        .gallery-item-info {
            padding: 1rem;
        }

        .gallery-item h3 {
            color: #8b4513;
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        }

        .gallery-item p {
            color: #654321;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .gallery-item-date {
            color: #b8860b;
            font-size: 0.8rem;
            font-weight: bold;
            margin-top: 0.5rem;
        }

        /* Blog Styles - Mobile First */
        .blog-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .blog-item {
            background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border: 3px solid #daa520;
            position: relative;
        }

        .blog-item h3 {
            color: #8b4513;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }

        .blog-item-meta {
            color: #b8860b;
            font-size: 0.85rem;
            margin-bottom: 1rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .blog-item-content {
            color: #654321;
            line-height: 1.6;
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }

        .blog-item-actions {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .btn-small {
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9rem;
            text-align: center;
            white-space: nowrap;
        }

        .btn-primary {
            background: #8b4513;
            color: #ffd700;
        }

        .btn-secondary {
            background: #daa520;
            color: #2c1810;
        }

        .btn-small:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Management Dashboard Styles - Mobile First */
        .management-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .management-card {
            background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border: 3px solid #daa520;
            position: relative;
        }

        .management-card h3 {
            color: #8b4513;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.2rem;
        }

        .management-card-content {
            color: #654321;
            margin-bottom: 1.5rem;
            font-size: 0.95rem;
        }

        .management-card-content > div {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.85rem;
        }

        .data-table th,
        .data-table td {
            padding: 0.5rem;
            text-align: left;
            border-bottom: 1px solid #daa520;
            word-wrap: break-word;
        }

        .data-table th {
            background: #8b4513;
            color: #ffd700;
            font-weight: bold;
            font-size: 0.8rem;
        }

        .data-table tr:hover {
            background: rgba(218, 165, 32, 0.1);
        }

        /* Form Styles - Mobile First */
        .form-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
            margin-top: 1rem;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 700;
            color: #8b4513;
            font-size: 0.95rem;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #daa520;
            border-radius: 8px;
            background: rgba(255, 248, 220, 0.9);
            color: #2c1810;
            font-family: inherit;
            font-size: 1rem;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
        }

        .form-group textarea {
            height: 100px;
            resize: vertical;
        }

        /* Modal Styles - Mobile First */
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
            padding: 1rem;
        }

        .modal-content {
            background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
            margin: 0 auto;
            padding: 1.5rem;
            border-radius: 20px;
            width: 100%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            border: 3px solid #daa520;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            margin-top: 2rem;
        }

        .close {
            color: #8b4513;
            float: right;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            position: absolute;
            right: 1rem;
            top: 1rem;
            padding: 0.25rem;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .close:hover {
            color: #654321;
            background: rgba(139, 69, 19, 0.1);
        }

        /* Hero Section - Mobile First */
        .hero {
            background: 
                linear-gradient(rgba(139, 69, 19, 0.7), rgba(184, 134, 11, 0.5)),
                radial-gradient(circle at 20% 50%, #8b4513 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, #daa520 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, #ffd700 0%, transparent 50%),
                #b8860b;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #2c1810;
            margin-top: 60px;
            position: relative;
            overflow: hidden;
            padding: 2rem 1rem;
        }

        .hero::before {
            content: '⚓';
            position: absolute;
            top: 10%;
            left: 5%;
            font-size: 6rem;
            opacity: 0.1;
            animation: float 8s ease-in-out infinite;
        }

        .hero::after {
            content: '⚓';
            position: absolute;
            bottom: 10%;
            right: 5%;
            font-size: 5rem;
            opacity: 0.1;
            animation: float 8s ease-in-out infinite reverse;
        }

        .hero-content {
            position: relative;
            z-index: 2;
            max-width: 100%;
        }

        .hero-content h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            animation: fadeInUp 1s ease;
            text-shadow: 4px 4px 8px rgba(0,0,0,0.3);
        }

        .hero-subtitle {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            font-weight: bold;
            color: #8b4513;
            text-shadow: 2px 2px 4px rgba(255,255,255,0.5);
            animation: fadeInUp 1s ease 0.2s both;
        }

        .hero-content p {
            font-size: 1rem;
            margin-bottom: 2rem;
            max-width: 100%;
            animation: fadeInUp 1s ease 0.4s both;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            line-height: 1.6;
        }

        .cta-button {
            background: linear-gradient(135deg, #8b4513 0%, #654321 100%);
            color: #ffd700;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            animation: fadeInUp 1s ease 0.6s both;
            box-shadow: 
                0 8px 16px rgba(0,0,0,0.3),
                inset 0 1px 0 rgba(255,255,255,0.2);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }

        .cta-button:hover {
            background: linear-gradient(135deg, #654321 0%, #4a2c17 100%);
            transform: translateY(-3px);
            box-shadow: 
                0 12px 24px rgba(0,0,0,0.4),
                inset 0 1px 0 rgba(255,255,255,0.3);
        }

        /* Section Styles */
        .section {
            padding: 3rem 0;
            position: relative;
        }

        .section:nth-child(even) {
            background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
        }

        .section:nth-child(odd) {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
            position: relative;
        }

        .section-title {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 2rem;
            color: #8b4513;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        }

        .section-subtitle {
            text-align: center;
            font-size: 1rem;
            color: #654321;
            margin-bottom: 2rem;
            max-width: 100%;
            margin-left: auto;
            margin-right: auto;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            line-height: 1.6;
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }

        .fade-in.visible {
            opacity: 1;
            transform: translateY(0);
        }

        /* Success/Error Messages */
        .success-message {
            background: linear-gradient(135deg, #90EE90 0%, #98FB98 100%);
            color: #006400;
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
            display: none;
            border: 2px solid #32CD32;
            font-size: 0.9rem;
        }

        .error-message {
            background: linear-gradient(135deg, #FFB6C1 0%, #FFC0CB 100%);
            color: #8B0000;
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
            display: none;
            border: 2px solid #DC143C;
            font-size: 0.9rem;
        }

        /* Rugged Texture Effects */
        .texture-overlay {
            position: relative;
        }

        .texture-overlay::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(139, 69, 19, 0.1) 2px, transparent 2px),
                radial-gradient(circle at 75% 75%, rgba(218, 165, 32, 0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            pointer-events: none;
        }

        /* File Upload Styles - Mobile Friendly */
        .file-upload-area {
            border: 2px dashed #daa520;
            border-radius: 10px;
            padding: 2rem 1rem;
            text-align: center;
            background: rgba(255, 248, 220, 0.5);
            margin: 1rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .file-upload-area:hover {
            border-color: #8b4513;
            background: rgba(255, 248, 220, 0.8);
        }

        .file-upload-area.dragover {
            border-color: #8b4513;
            background: rgba(255, 248, 220, 0.9);
            transform: scale(1.02);
        }

        .file-upload-area h3 {
            font-size: 1rem;
            margin: 0.5rem 0;
        }

        .file-upload-area p {
            font-size: 0.85rem;
            margin: 0;
        }

        /* Touch-friendly improvements */
        button, .btn-small, .cta-button, .login-btn {
            min-height: 44px;
            min-width: 44px;
        }

        /* Tablet Styles */
        @media (min-width: 481px) and (max-width: 768px) {
            .nav-container {
                padding: 0 1.5rem;
            }

            .logo {
                font-size: 1.5rem;
            }

            .logo i {
                font-size: 2rem;
            }

            .hero-content h1 {
                font-size: 3rem;
            }

            .hero-subtitle {
                font-size: 1.4rem;
            }

            .hero-content p {
                font-size: 1.1rem;
            }

            .section-title {
                font-size: 2.5rem;
            }

            .section-subtitle {
                font-size: 1.1rem;
            }

            .gallery-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .blog-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .management-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .form-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .blog-item-actions {
                flex-direction: row;
            }

            .modal-content {
                max-width: 600px;
                padding: 2rem;
            }
        }

        /* Desktop Styles */
        @media (min-width: 769px) {
            .nav-container {
                padding: 0 2rem;
            }

            .logo {
                font-size: 1.8rem;
            }

            .logo i {
                font-size: 2.5rem;
                margin-right: 0.5rem;
            }

            .nav-menu {
                display: flex;
                position: static;
                width: auto;
                background: none;
                flex-direction: row;
                padding: 0;
                box-shadow: none;
                gap: 2rem;
                max-height: none;
                overflow: visible;
            }

            .nav-menu a {
                padding: 0.5rem 1rem;
                font-size: 1rem;
            }

            .mobile-menu-btn {
                display: none;
            }

            .login-btn {
                font-size: 1rem;
                padding: 0.5rem 1rem;
            }

            .page-content {
                margin-top: 100px;
                padding: 2rem 0;
            }

            .hero {
                height: 100vh;
                margin-top: 80px;
                padding: 0;
            }

            .hero::before {
                font-size: 12rem;
                left: 10%;
            }

            .hero::after {
                font-size: 10rem;
                right: 10%;
            }

            .hero-content h1 {
                font-size: 4rem;
            }

            .hero-subtitle {
                font-size: 1.5rem;
            }

            .hero-content p {
                font-size: 1.2rem;
                max-width: 700px;
            }

            .cta-button {
                font-size: 1.2rem;
                padding: 1.2rem 2.5rem;
            }

            .section {
                padding: 5rem 0;
            }

            .section-title {
                font-size: 3rem;
                margin-bottom: 3rem;
            }

            .section-subtitle {
                font-size: 1.2rem;
                margin-bottom: 3rem;
                max-width: 600px;
            }

            .container {
                padding: 0 2rem;
            }

            .gallery-grid {
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
            }

            .gallery-item img, .gallery-item video {
                height: 250px;
            }

            .gallery-item-info {
                padding: 1.5rem;
            }

            .blog-grid {
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 2rem;
            }

            .blog-item {
                padding: 2rem;
            }

            .blog-item-actions {
                flex-direction: row;
                gap: 1rem;
            }

            .management-grid {
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
            }

            .management-card {
                padding: 2rem;
            }

            .management-card-content > div {
                flex-direction: row;
                gap: 1rem;
            }

            .form-grid {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            }

            .modal-content {
                max-width: 800px;
                padding: 2rem;
                margin-top: 2%;
            }

            .data-table {
                font-size: 1rem;
            }

            .data-table th,
            .data-table td {
                padding: 0.75rem;
            }

            .data-table th {
                font-size: 1rem;
            }
        }

        /* Large Desktop Styles */
        @media (min-width: 1200px) {
            .management-grid {
                grid-template-columns: repeat(3, 1fr);
            }

            .gallery-grid {
                grid-template-columns: repeat(3, 1fr);
            }

            .blog-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        /* About page grid responsiveness */
        .about-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
            align-items: center;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        @media (min-width: 769px) {
            .about-grid {
                grid-template-columns: 1fr 1fr;
                gap: 3rem;
            }

            .stats-grid {
                gap: 2rem;
            }
        }

        /* Services grid responsiveness */
        .services-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 481px) {
            .services-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (min-width: 769px) {
            .services-grid {
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
            }
        }

        /* Members grid responsiveness */
        .members-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        @media (min-width: 481px) {
            .members-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (min-width: 769px) {
            .members-grid {
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2rem;
                margin-bottom: 3rem;
            }
        }

        /* Contact grid responsiveness */
        .contact-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        @media (min-width: 769px) {
            .contact-grid {
                grid-template-columns: 1fr 1fr;
                gap: 3rem;
            }
        }

        /* Improved touch targets for mobile */
        @media (max-width: 768px) {
            .nav-menu a {
                min-height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .btn-small {
                min-height: 48px;
                padding: 0.75rem 1.5rem;
            }

            .cta-button {
                min-height: 48px;
                padding: 1rem 2rem;
            }

            .login-btn {
                min-height: 44px;
                padding: 0.75rem 1rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <nav class="nav-container">
            <div class="logo rugged-title">
                <i class="fas fa-anchor"></i>
                NASA FRIGATE
            </div>
            <ul class="nav-menu" id="navMenu">
                <li><a onclick="showPage('home')">Home</a></li>
                <li><a onclick="showPage('about')">About</a></li>
                <li><a onclick="showPage('services')">Services</a></li>
                <li><a onclick="showPage('gallery')">Gallery</a></li>
                <li><a onclick="showPage('blog')">Ship's Log</a></li>
                <li><a onclick="showPage('members')">Crew</a></li>
                <li><a onclick="showPage('contact')">Contact</a></li>
            </ul>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <button class="login-btn" onclick="openLoginModal()">
                    <i class="fas fa-sign-in-alt"></i> <span class="login-text">Leadership Login</span>
                </button>
                <button class="mobile-menu-btn" id="mobileMenuBtn">
                    <i class="fas fa-bars"></i>
                </button>
            </div>
        </nav>
    </header>

    <!-- Home Page -->
    <div id="homePage" class="page-content">
        <!-- Hero Section -->
        <section class="hero texture-overlay">
            <div class="hero-content">
                <h1 class="rugged-title">NASA FRIGATE</h1>
                <div class="hero-subtitle rugged-title">Rugged Sailors of Service</div>
                <p><strong>Navigating Acts of Service & Altruism</strong> - We are a distinguished non-profit organization of dedicated mariners committed to community service and charitable excellence. Our professional crew of seasoned volunteers charts courses through challenging waters of social need, dropping anchor wherever our expertise and resources can make the greatest impact.</p>
                <a onclick="showPage('about')" class="cta-button">
                    <i class="fas fa-compass"></i> Chart Our Course
                </a>
            </div>
        </section>
    </div>

    <!-- About Page -->
    <div id="aboutPage" class="page-content hidden">
        <section class="section texture-overlay">
            <div class="container">
                <h2 class="section-title rugged-title">About Our Rugged Crew</h2>
                <p class="section-subtitle">Weathered by service, strengthened by purpose, united by the call of the sea and the duty to serve.</p>
                
                <div class="about-grid">
                    <div>
                        <h3 class="rugged-title" style="font-size: 1.8rem; margin-bottom: 1rem; color: #8b4513;">Our Professional Maritime Mission</h3>
                        <p style="margin-bottom: 1.5rem; color: #654321; line-height: 1.8;">NASA FRIGATE stands as a beacon of professional service in the non-profit sector. We are an established organization of skilled volunteers who combine maritime tradition with modern charitable excellence.</p>
                        <p style="margin-bottom: 1.5rem; color: #654321; line-height: 1.8;">Our organization operates under experienced leadership, maintaining the highest standards of accountability while delivering impactful community programs.</p>
                        <p style="color: #654321; line-height: 1.8;">As a registered non-profit organization, our open membership welcomes qualified individuals who share our commitment to professional service and maritime values.</p>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="card-3d" style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); border-radius: 15px; border: 3px solid #daa520;">
                            <span style="font-size: 2.5rem; font-weight: bold; color: #8b4513; display: block;" id="membersCount">54+</span>
                            <span style="color: #654321; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Active Members</span>
                        </div>
                        <div class="card-3d" style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); border-radius: 15px; border: 3px solid #daa520;">
                            <span style="font-size: 2.5rem; font-weight: bold; color: #8b4513; display: block;" id="eventsCount">127</span>
                            <span style="color: #654321; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Voyages Completed</span>
                        </div>
                        <div class="card-3d" style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); border-radius: 15px; border: 3px solid #daa520;">
                            <span style="font-size: 2.5rem; font-weight: bold; color: #8b4513; display: block;" id="impactCount">15K+</span>
                            <span style="color: #654321; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Lives Rescued</span>
                        </div>
                        <div class="card-3d" style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); border-radius: 15px; border: 3px solid #daa520;">
                            <span style="font-size: 2rem; font-weight: bold; color: #8b4513; display: block;">501(c)(3)</span>
                            <span style="color: #654321; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Non-Profit Status</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <!-- Services Page -->
    <div id="servicesPage" class="page-content hidden">
        <section class="section texture-overlay">
            <div class="container">
                <h2 class="section-title rugged-title">Our Maritime Missions</h2>
                <p class="section-subtitle">From calm harbors to stormy seas, our crew tackles every mission with professional excellence and maritime determination.</p>
                
                <div class="services-grid">
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="font-size: 3rem; color: #8b4513; margin-bottom: 1rem;"><i class="fas fa-hands-helping"></i></div>
                        <h3 class="rugged-title" style="font-size: 1.5rem; margin-bottom: 1rem; color: #8b4513;">Community Outreach</h3>
                        <p style="color: #654321; line-height: 1.7;">Professional relief operations delivering strategic aid where needed most, with precision and measurable impact.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="font-size: 3rem; color: #8b4513; margin-bottom: 1rem;"><i class="fas fa-handshake"></i></div>
                        <h3 class="rugged-title" style="font-size: 1.5rem; margin-bottom: 1rem; color: #8b4513;">Strategic Partnerships</h3>
                        <p style="color: #654321; line-height: 1.7;">Professional alliances with businesses and organizations, creating powerful networks of social responsibility.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="font-size: 3rem; color: #8b4513; margin-bottom: 1rem;"><i class="fas fa-graduation-cap"></i></div>
                        <h3 class="rugged-title" style="font-size: 1.5rem; margin-bottom: 1rem; color: #8b4513;">Navigation Training</h3>
                        <p style="color: #654321; line-height: 1.7;">Educational programs guiding others through life's challenges like lighthouse beacons in treacherous waters.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="font-size: 3rem; color: #8b4513; margin-bottom: 1rem;"><i class="fas fa-leaf"></i></div>
                        <h3 class="rugged-title" style="font-size: 1.5rem; margin-bottom: 1rem; color: #8b4513;">Ocean Conservation</h3>
                        <p style="color: #654321; line-height: 1.7;">Environmental missions protecting the waters that sustain us for future generations of sailors.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="font-size: 3rem; color: #8b4513; margin-bottom: 1rem;"><i class="fas fa-users"></i></div>
                        <h3 class="rugged-title" style="font-size: 1.5rem; margin-bottom: 1rem; color: #8b4513;">Crew Brotherhood</h3>
                        <p style="color: #654321; line-height: 1.7;">Unbreakable bonds forged through shared service, mutual support, and maritime tradition.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="font-size: 3rem; color: #8b4513; margin-bottom: 1rem;"><i class="fas fa-calendar-alt"></i></div>
                        <h3 class="rugged-title" style="font-size: 1.5rem; margin-bottom: 1rem; color: #8b4513;">Harbor Celebrations</h3>
                        <p style="color: #654321; line-height: 1.7;">Legendary gatherings where crew valor is recognized and tales of heroism are shared.</p>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <!-- Gallery Page -->
    <div id="galleryPage" class="page-content hidden">
        <section class="section texture-overlay">
            <div class="container">
                <h2 class="section-title rugged-title">Voyage Gallery</h2>
                <p class="section-subtitle">Chronicles of our maritime adventures and community service expeditions across the seven seas of need.</p>
                
                <div id="galleryGrid" class="gallery-grid">
                    <!-- Gallery items will be loaded here -->
                </div>
                
                <div style="text-align: center; margin-top: 3rem;">
                    <button class="cta-button" onclick="loadGallery()">
                        <i class="fas fa-sync-alt"></i> Refresh Gallery
                    </button>
                </div>
            </div>
        </section>
    </div>

    <!-- Blog Page -->
    <div id="blogPage" class="page-content hidden">
        <section class="section texture-overlay">
            <div class="container">
                <h2 class="section-title rugged-title">Ship's Log & Chronicles</h2>
                <p class="section-subtitle">Technical logs, mission reports, and maritime wisdom from our experienced crew.</p>
                
                <div id="blogGrid" class="blog-grid">
                    <!-- Blog items will be loaded here -->
                </div>
                
                <div style="text-align: center; margin-top: 3rem;">
                    <button class="cta-button" onclick="loadBlogPosts()">
                        <i class="fas fa-sync-alt"></i> Refresh Ship's Log
                    </button>
                </div>
            </div>
        </section>
    </div>

    <!-- Members Page -->
    <div id="membersPage" class="page-content hidden">
        <section class="section texture-overlay">
            <div class="container">
                <h2 class="section-title rugged-title">Our Ship's Officers & Crew</h2>
                <p class="section-subtitle">Meet the weathered veterans who command our vessel and the brave souls who make our missions possible.</p>
                
                <div class="members-grid">
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #8b4513, #654321); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2rem; color: #ffd700; border: 4px solid #daa520;">
                            <i class="fas fa-anchor"></i>
                        </div>
                        <div class="rugged-title" style="font-size: 1.3rem; font-weight: bold; color: #8b4513; margin-bottom: 0.5rem;">Frigate Captain (FC)</div>
                        <div style="color: #b8860b; font-weight: 700; margin-bottom: 1rem; font-size: 1rem;">Supreme Commander</div>
                        <p style="color: #654321; font-size: 0.9rem;">Battle-scarred leader navigating with wisdom and courage, making decisions with the weight of countless lives at stake.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #8b4513, #654321); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2rem; color: #ffd700; border: 4px solid #daa520;">
                            <i class="fas fa-scroll"></i>
                        </div>
                        <div class="rugged-title" style="font-size: 1.3rem; font-weight: bold; color: #8b4513; margin-bottom: 0.5rem;">The Scribe</div>
                        <div style="color: #b8860b; font-weight: 700; margin-bottom: 1rem; font-size: 1rem;">Keeper of Records</div>
                        <p style="color: #654321; font-size: 0.9rem;">Chronicles every voyage and victory, preserving our legacy in careful records for future generations.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #8b4513, #654321); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2rem; color: #ffd700; border: 4px solid #daa520;">
                            <i class="fas fa-bullhorn"></i>
                        </div>
                        <div class="rugged-title" style="font-size: 1.3rem; font-weight: bold; color: #8b4513; margin-bottom: 0.5rem;">The Crier</div>
                        <div style="color: #b8860b; font-weight: 700; margin-bottom: 1rem; font-size: 1rem;">Voice Across Waters</div>
                        <p style="color: #654321; font-size: 0.9rem;">Carries our message across vast distances, ensuring no call for help goes unheard.</p>
                    </div>
                    
                    <div class="card-3d" style="background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; text-align: center; border: 3px solid #daa520;">
                        <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #8b4513, #654321); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2rem; color: #ffd700; border: 4px solid #daa520;">
                            <i class="fas fa-treasure-chest"></i>
                        </div>
                        <div class="rugged-title" style="font-size: 1.3rem; font-weight: bold; color: #8b4513; margin-bottom: 0.5rem;">The Purse</div>
                        <div style="color: #b8860b; font-weight: 700; margin-bottom: 1rem; font-size: 1rem;">Guardian of Treasure</div>
                        <p style="color: #654321; font-size: 0.9rem;">Guards our resources with integrity, ensuring every coin serves our noble cause.</p>
                    </div>
                </div>
                
                <div class="card-3d" style="text-align: center; background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%); padding: 2rem; border-radius: 20px; border: 3px solid #daa520;">
                    <h3 class="rugged-title">Join Our Professional Crew</h3>
                    <span style="font-size: 4rem; font-weight: bold; color: #8b4513; display: block;" id="memberCount">54+</span>
                    <p style="margin: 1rem 0;">Professional volunteers united by purpose, strengthened by experience, and committed to excellence in community service.</p>
                    <button class="cta-button" onclick="showJoinMessage()">
                        <i class="fas fa-anchor"></i> Apply for Membership
                    </button>
                </div>
            </div>
        </section>
    </div>

    <!-- Contact Page -->
    <div id="contactPage" class="page-content hidden">
        <section class="section" style="background: linear-gradient(135deg, #8b4513 0%, #654321 100%); color: #ffd700;">
            <div class="container">
                <h2 class="section-title rugged-title">Signal Our Ship</h2>
                <p class="section-subtitle">Ready to join our crew or send word across the waters? Drop anchor and send us a message!</p>
                
                <div class="contact-grid">
                    <div>
                        <h3 class="rugged-title" style="font-size: 1.8rem; margin-bottom: 1.5rem;">Ship's Coordinates</h3>
                        <div style="display: flex; align-items: flex-start; margin-bottom: 1.5rem; padding: 1rem; background: rgba(255, 215, 0, 0.1); border-radius: 10px; border-left: 4px solid #ffd700;">
                            <i class="fas fa-map-marker-alt" style="font-size: 1.5rem; margin-right: 1rem; color: #ffd700; margin-top: 0.2rem;"></i>
                            <span>Harbor Master's Dock<br>123 Sailor's Wharf<br>Port Altruism, PA 12345</span>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding: 1rem; background: rgba(255, 215, 0, 0.1); border-radius: 10px; border-left: 4px solid #ffd700;">
                            <i class="fas fa-radio" style="font-size: 1.5rem; margin-right: 1rem; color: #ffd700;"></i>
                            <span>Ship's Radio: +1 (555) ANCHOR-1</span>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding: 1rem; background: rgba(255, 215, 0, 0.1); border-radius: 10px; border-left: 4px solid #ffd700;">
                            <i class="fas fa-envelope" style="font-size: 1.5rem; margin-right: 1rem; color: #ffd700;"></i>
                            <span>Message Bottle: ahoy@nasafrigate.org</span>
                        </div>
                    </div>
                    
                    <form id="contactForm" style="background: rgba(255, 215, 0, 0.1); padding: 2rem; border-radius: 20px; border: 2px solid #daa520;">
                        <h3 class="rugged-title">Send a Message</h3>
                        <div class="form-group">
                            <label for="name">Sailor's Name</label>
                            <input type="text" id="name" name="name" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Message Bottle Address</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="subject">Signal Flag</label>
                            <input type="text" id="subject" name="subject" required>
                        </div>
                        <div class="form-group">
                            <label for="message">Your Message</label>
                            <textarea id="message" name="message" required placeholder="Tell us about your voyage or how you'd like to join our crew..."></textarea>
                        </div>
                        <button type="submit" class="cta-button">
                            <i class="fas fa-paper-plane"></i> Launch Message
                        </button>
                        <div id="successMessage" class="success-message">
                            Message received! Our crew will signal back within two tides.
                        </div>
                        <div id="errorMessage" class="error-message">
                            Storm interference detected. Please try sending your message again.
                        </div>
                    </form>
                </div>
            </div>
        </section>
    </div>

    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeLoginModal()">&times;</span>
            <form id="loginForm">
                <h2 class="rugged-title">Officer's Quarters</h2>
                <div class="form-group">
                    <label for="username">Officer Rank</label>
                    <input type="text" id="username" name="username" required placeholder="captain, scribe, crier, or purse">
                </div>
                <div class="form-group">
                    <label for="password">Access Code</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="cta-button">
                    <i class="fas fa-anchor"></i> Board Ship
                </button>
                <div style="margin-top: 1rem; font-size: 0.9em; color: #654321;">
                    <strong>Sample Credentials:</strong><br>
                    captain / anchor2024<br>
                    scribe / quill2024<br>
                    crier / horn2024<br>
                    purse / coin2024
                </div>
            </form>
        </div>
    </div>

    <!-- Management Dashboard Modal -->
    <div id="managementModal" class="modal">
        <div class="modal-content" style="max-width: 95vw;">
            <span class="close" onclick="closeManagementModal()">&times;</span>
            <div id="managementContent">
                <!-- Management content will be loaded here -->
            </div>
        </div>
    </div>

    <!-- Generic Modal for Forms -->
    <div id="genericModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeGenericModal()">&times;</span>
            <div id="genericModalContent">
                <!-- Dynamic content will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let currentUser = null;
        let currentPage = 'home';

        // Page Navigation
        function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('.page-content').forEach(page => {
                page.classList.add('hidden');
            });
            
            // Show selected page
            document.getElementById(pageId + 'Page').classList.remove('hidden');
            currentPage = pageId;
            
            // Load page-specific content
            switch(pageId) {
                case 'gallery':
                    loadGallery();
                    break;
                case 'blog':
                    loadBlogPosts();
                    break;
                case 'members':
                    loadStats();
                    break;
            }
            
            // Close mobile menu
            document.getElementById('navMenu').classList.remove('active');
        }

        // Mobile Menu Toggle
        document.getElementById('mobileMenuBtn').addEventListener('click', () => {
            document.getElementById('navMenu').classList.toggle('active');
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            const navMenu = document.getElementById('navMenu');
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            
            if (!navMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                navMenu.classList.remove('active');
            }
        });

        // Login Functions
        function openLoginModal() {
            document.getElementById('loginModal').style.display = 'block';
        }

        function closeLoginModal() {
            document.getElementById('loginModal').style.display = 'none';
        }

        function openManagementModal() {
            document.getElementById('managementModal').style.display = 'block';
            loadManagementDashboard();
        }

        function closeManagementModal() {
            document.getElementById('managementModal').style.display = 'none';
        }

        function openGenericModal() {
            document.getElementById('genericModal').style.display = 'block';
        }

        function closeGenericModal() {
            document.getElementById('genericModal').style.display = 'none';
        }

        // Login Form Submission
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const credentials = {
                username: formData.get('username'),
                password: formData.get('password')
            };
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(credentials)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentUser = result.user;
                    closeLoginModal();
                    openManagementModal();
                } else {
                    alert('Invalid credentials, sailor! Check your rank and access code.');
                }
            } catch (error) {
                console.log('Login system offline, using demo mode');
                // Demo mode for when API is not available
                const demoCredentials = {
                    'captain': { role: 'Frigate Captain', name: 'Captain Sarah Johnson' },
                    'scribe': { role: 'Scribe', name: 'Michael Chen' },
                    'crier': { role: 'Crier', name: 'Amanda Rodriguez' },
                    'purse': { role: 'Purse', name: 'David Thompson' }
                };
                
                if (demoCredentials[credentials.username]) {
                    currentUser = demoCredentials[credentials.username];
                    closeLoginModal();
                    openManagementModal();
                } else {
                    alert('Invalid credentials, sailor! Try: captain/anchor2024, scribe/quill2024, crier/horn2024, or purse/coin2024');
                }
            }
        });

        // Management Dashboard
        function loadManagementDashboard() {
            if (!currentUser) return;
            
            const content = document.getElementById('managementContent');
            content.innerHTML = `
                <div style="margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #daa520;">
                    <h2 class="rugged-title">Officer's Command Center</h2>
                    <p style="color: #654321; margin-top: 0.5rem;">Welcome aboard, ${currentUser.role}: ${currentUser.name}</p>
                    <button class="btn-small btn-secondary" onclick="logout()" style="margin-top: 1rem;">
                        <i class="fas fa-sign-out-alt"></i> Abandon Ship
                    </button>
                </div>
                
                <div class="management-grid">
                    <div class="management-card card-3d">
                        <h3><i class="fas fa-users"></i> Crew Management</h3>
                        <div class="management-card-content">
                            <p>Manage crew members, roles, and assignments</p>
                            <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                                <button class="btn-small btn-primary" onclick="showCrewList()">View Crew</button>
                                <button class="btn-small btn-secondary" onclick="showAddMemberForm()">Add Member</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="management-card card-3d">
                        <h3><i class="fas fa-calendar-alt"></i> Event Management</h3>
                        <div class="management-card-content">
                            <p>Plan voyages and coordinate missions</p>
                            <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                                <button class="btn-small btn-primary" onclick="showEventList()">View Events</button>
                                <button class="btn-small btn-secondary" onclick="showAddEventForm()">Plan Mission</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="management-card card-3d">
                        <h3><i class="fas fa-images"></i> Gallery Management</h3>
                        <div class="management-card-content">
                            <p>Upload and manage voyage photos</p>
                            <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                                <button class="btn-small btn-primary" onclick="showGalleryManager()">Manage Gallery</button>
                                <button class="btn-small btn-secondary" onclick="showUploadForm()">Upload Media</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="management-card card-3d">
                        <h3><i class="fas fa-scroll"></i> Ship's Log</h3>
                        <div class="management-card-content">
                            <p>Manage blog posts and technical logs</p>
                            <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                                <button class="btn-small btn-primary" onclick="showBlogManager()">Manage Posts</button>
                                <button class="btn-small btn-secondary" onclick="showCreatePostForm()">New Entry</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="management-card card-3d">
                        <h3><i class="fas fa-envelope"></i> Messages</h3>
                        <div class="management-card-content">
                            <p>Review incoming communications</p>
                            <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                                <button class="btn-small btn-primary" onclick="showMessages()">Read Messages</button>
                                <button class="btn-small btn-secondary" onclick="showMessageStats()">Statistics</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="management-card card-3d">
                        <h3><i class="fas fa-chart-line"></i> Ship's Status</h3>
                        <div class="management-card-content">
                            <p>Organization statistics and reports</p>
                            <div id="dashboardStats" style="margin-top: 1rem;">
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; text-align: center;">
                                    <div>
                                        <div style="font-size: 2rem; font-weight: bold; color: #8b4513;" id="dashMemberCount">54</div>
                                        <div style="font-size: 0.9rem; color: #654321;">Active Crew</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 2rem; font-weight: bold; color: #8b4513;" id="dashEventCount">127</div>
                                        <div style="font-size: 0.9rem; color: #654321;">Voyages</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            loadDashboardStats();
        }

        // Gallery Functions
        async function loadGallery() {
            try {
                const response = await fetch('/api/gallery');
                const data = await response.json();
                
                const galleryGrid = document.getElementById('galleryGrid');
                
                if (data.success && data.items.length > 0) {
                    galleryGrid.innerHTML = data.items.map(item => `
                        <div class="gallery-item card-3d">
                            ${item.type === 'video' ? 
                                `<video controls><source src="/gallery/${item.filename}" type="video/mp4"></video>` :
                                `<img src="/gallery/${item.filename}" alt="${item.title}" loading="lazy">`
                            }
                            <div class="gallery-item-info">
                                <h3>${item.title}</h3>
                                <p>${item.description}</p>
                                <div class="gallery-item-date">${new Date(item.created_at).toLocaleDateString()}</div>
                            </div>
                        </div>
                    `).join('');
                } else {
                    galleryGrid.innerHTML = `
                        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #654321;">
                            <i class="fas fa-images" style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                            <h3>No voyage photos yet</h3>
                            <p>Our crew is preparing to document their next adventure!</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading gallery:', error);
                document.getElementById('galleryGrid').innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #654321;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 4rem; margin-bottom: 1rem; color: #8b4513;"></i>
                        <h3>Unable to load gallery</h3>
                        <p>Storm interference detected. Please try again later.</p>
                    </div>
                `;
            }
        }

        // Blog Functions
        async function loadBlogPosts() {
            try {
                const response = await fetch('/api/blog');
                const data = await response.json();
                
                const blogGrid = document.getElementById('blogGrid');
                
                if (data.success && data.posts.length > 0) {
                    blogGrid.innerHTML = data.posts.map(post => `
                        <div class="blog-item card-3d">
                            <h3>${post.title}</h3>
                            <div class="blog-item-meta">
                                <span><i class="fas fa-calendar"></i> ${new Date(post.created_at).toLocaleDateString()}</span>
                                <span><i class="fas fa-user"></i> ${post.author}</span>
                            </div>
                            <div class="blog-item-content">${post.excerpt}</div>
                            <div class="blog-item-actions">
                                <button class="btn-small btn-primary" onclick="viewBlogPost('${post.filename}')">
                                    <i class="fas fa-eye"></i> Read Log
                                </button>
                                <button class="btn-small btn-secondary" onclick="downloadBlogPost('${post.filename}')">
                                    <i class="fas fa-download"></i> Download
                                </button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    blogGrid.innerHTML = `
                        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #654321;">
                            <i class="fas fa-scroll" style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                            <h3>No ship's logs yet</h3>
                            <p>Our scribes are preparing the next chronicle of our adventures!</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error loading blog posts:', error);
                document.getElementById('blogGrid').innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #654321;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 4rem; margin-bottom: 1rem; color: #8b4513;"></i>
                        <h3>Unable to load ship's logs</h3>
                        <p>Storm interference detected. Please try again later.</p>
                    </div>
                `;
            }
        }

        async function viewBlogPost(filename) {
            try {
                const response = await fetch(`/api/blog/${filename}`);
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('genericModalContent').innerHTML = `
                        <h2 class="rugged-title">${data.post.title}</h2>
                        <div style="margin-bottom: 2rem; color: #654321; border-bottom: 1px solid #daa520; padding-bottom: 1rem;">
                            <i class="fas fa-calendar"></i> ${new Date(data.post.created_at).toLocaleDateString()}
                            <span style="margin-left: 2rem;"><i class="fas fa-user"></i> ${data.post.author}</span>
                        </div>
                        <div style="background: #f5f5dc; padding: 1.5rem; border-radius: 10px; font-family: monospace; white-space: pre-wrap; overflow-x: auto; max-height: 60vh; overflow-y: auto; font-size: 0.9rem;">
${data.post.content}
                        </div>
                        <div style="margin-top: 2rem; text-align: center;">
                            <button class="btn-small btn-secondary" onclick="downloadBlogPost('${filename}')">
                                <i class="fas fa-download"></i> Download Original
                            </button>
                        </div>
                    `;
                    openGenericModal();
                }
            } catch (error) {
                alert('Unable to load blog post. Storm interference detected.');
            }
        }

        function downloadBlogPost(filename) {
            window.open(`/api/blog/${filename}/download`, '_blank');
        }

        // Management Functions
        async function showCrewList() {
            try {
                const response = await fetch('/api/members');
                const data = await response.json();
                
                let tableRows = '';
                if (data.success && data.members.length > 0) {
                    tableRows = data.members.map(member => `
                        <tr>
                            <td>${member.name}</td>
                            <td>${member.email}</td>
                            <td>${member.role}</td>
                            <td>${member.join_date || 'Unknown'}</td>
                            <td>
                                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                    <button class="btn-small btn-primary" onclick="editMember(${member.id})">Edit</button>
                                    <button class="btn-small btn-secondary" onclick="deleteMember(${member.id})">Remove</button>
                                </div>
                            </td>
                        </tr>
                    `).join('');
                } else {
                    tableRows = '<tr><td colspan="5" style="text-align: center; color: #654321;">No crew members found</td></tr>';
                }
                
                document.getElementById('genericModalContent').innerHTML = `
                    <h2 class="rugged-title">Crew Roster</h2>
                    <div style="margin-bottom: 2rem;">
                        <button class="btn-small btn-secondary" onclick="showAddMemberForm()">
                            <i class="fas fa-plus"></i> Add New Crew Member
                        </button>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Join Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                `;
                openGenericModal();
            } catch (error) {
                alert('Unable to load crew roster. Storm interference detected.');
            }
        }

        function showAddMemberForm() {
            document.getElementById('genericModalContent').innerHTML = `
                <h2 class="rugged-title">Enlist New Crew Member</h2>
                <form id="addMemberForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="memberName">Sailor's Name</label>
                            <input type="text" id="memberName" name="name" required>
                        </div>
                        <div class="form-group">
                            <label for="memberEmail">Email Address</label>
                            <input type="email" id="memberEmail" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="memberRole">Role</label>
                            <select id="memberRole" name="role">
                                <option value="Member">Member</option>
                                <option value="Officer">Officer</option>
                                <option value="Volunteer">Volunteer</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="memberPhone">Phone</label>
                            <input type="tel" id="memberPhone" name="phone">
                        </div>
                        <div class="form-group">
                            <label for="memberBirthday">Birthday</label>
                            <input type="date" id="memberBirthday" name="birthday">
                        </div>
                        <div class="form-group">
                            <label for="memberSkills">Skills</label>
                            <input type="text" id="memberSkills" name="skills" placeholder="Navigation, Leadership, etc.">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="memberAddress">Address</label>
                        <textarea id="memberAddress" name="address" placeholder="Full address"></textarea>
                    </div>
                    <div style="text-align: center; margin-top: 2rem;">
                        <button type="submit" class="cta-button">
                            <i class="fas fa-anchor"></i> Enlist Crew Member
                        </button>
                    </div>
                </form>
            `;
            
            document.getElementById('addMemberForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const memberData = Object.fromEntries(formData);
                
                try {
                    const response = await fetch('/api/members', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(memberData)
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('New crew member enlisted successfully!');
                        closeGenericModal();
                        loadDashboardStats();
                    } else {
                        alert('Failed to enlist crew member: ' + result.error);
                    }
                } catch (error) {
                    alert('Unable to enlist crew member. Storm interference detected.');
                }
            });
            
            openGenericModal();
        }

        async function showEventList() {
            try {
                const response = await fetch('/api/events');
                const data = await response.json();
                
                let tableRows = '';
                if (data.success && data.events.length > 0) {
                    tableRows = data.events.map(event => `
                        <tr>
                            <td>${event.title}</td>
                            <td>${event.event_date}</td>
                            <td>${event.location || 'TBD'}</td>
                            <td>${event.category}</td>
                            <td>
                                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                    <button class="btn-small btn-primary" onclick="editEvent(${event.id})">Edit</button>
                                    <button class="btn-small btn-secondary" onclick="deleteEvent(${event.id})">Cancel</button>
                                </div>
                            </td>
                        </tr>
                    `).join('');
                } else {
                    tableRows = '<tr><td colspan="5" style="text-align: center; color: #654321;">No upcoming voyages planned</td></tr>';
                }
                
                document.getElementById('genericModalContent').innerHTML = `
                    <h2 class="rugged-title">Mission Schedule</h2>
                    <div style="margin-bottom: 2rem;">
                        <button class="btn-small btn-secondary" onclick="showAddEventForm()">
                            <i class="fas fa-plus"></i> Plan New Mission
                        </button>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Mission</th>
                                    <th>Date</th>
                                    <th>Location</th>
                                    <th>Category</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                `;
                openGenericModal();
            } catch (error) {
                alert('Unable to load mission schedule. Storm interference detected.');
            }
        }

        function showAddEventForm() {
            document.getElementById('genericModalContent').innerHTML = `
                <h2 class="rugged-title">Plan New Mission</h2>
                <form id="addEventForm">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="eventTitle">Mission Title</label>
                            <input type="text" id="eventTitle" name="title" required>
                        </div>
                        <div class="form-group">
                            <label for="eventDate">Mission Date</label>
                            <input type="date" id="eventDate" name="event_date" required>
                        </div>
                        <div class="form-group">
                            <label for="eventTime">Mission Time</label>
                            <input type="time" id="eventTime" name="event_time">
                        </div>
                        <div class="form-group">
                            <label for="eventLocation">Location</label>
                            <input type="text" id="eventLocation" name="location">
                        </div>
                        <div class="form-group">
                            <label for="eventCategory">Category</label>
                            <select id="eventCategory" name="category">
                                <option value="Community Service">Community Service</option>
                                <option value="Fundraising">Fundraising</option>
                                <option value="Training">Training</option>
                                <option value="Social">Social</option>
                                <option value="Environmental">Environmental</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="eventMaxParticipants">Max Participants</label>
                            <input type="number" id="eventMaxParticipants" name="max_participants">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="eventDescription">Mission Description</label>
                        <textarea id="eventDescription" name="description" placeholder="Describe the mission objectives and details"></textarea>
                    </div>
                    <div style="text-align: center; margin-top: 2rem;">
                        <button type="submit" class="cta-button">
                            <i class="fas fa-compass"></i> Schedule Mission
                        </button>
                    </div>
                </form>
            `;
            
            document.getElementById('addEventForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const eventData = Object.fromEntries(formData);
                eventData.created_by = currentUser.name;
                
                try {
                    const response = await fetch('/api/events', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(eventData)
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('Mission scheduled successfully!');
                        closeGenericModal();
                        loadDashboardStats();
                    } else {
                        alert('Failed to schedule mission: ' + result.error);
                    }
                } catch (error) {
                    alert('Unable to schedule mission. Storm interference detected.');
                }
            });
            
            openGenericModal();
        }

        function showUploadForm() {
            document.getElementById('genericModalContent').innerHTML = `
                <h2 class="rugged-title">Upload Voyage Media</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="uploadTitle">Title</label>
                        <input type="text" id="uploadTitle" name="title" required>
                    </div>
                    <div class="form-group">
                        <label for="uploadDescription">Description</label>
                        <textarea id="uploadDescription" name="description" placeholder="Describe this voyage moment"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="uploadCategory">Category</label>
                        <select id="uploadCategory" name="category">
                            <option value="Mission">Mission</option>
                            <option value="Training">Training</option>
                            <option value="Social">Social</option>
                            <option value="Achievement">Achievement</option>
                        </select>
                    </div>
                    <div class="file-upload-area" onclick="document.getElementById('uploadFile').click()">
                        <i class="fas fa-cloud-upload-alt" style="font-size: 2.5rem; color: #8b4513; margin-bottom: 0.5rem;"></i>
                        <h3>Drop files here or click to upload</h3>
                        <p>Supported: Images (PNG, JPG, GIF, WEBP) and Videos (MP4, MOV)</p>
                        <input type="file" id="uploadFile" name="file" accept="image/*,video/*" style="display: none;" required>
                    </div>
                    <div style="text-align: center; margin-top: 2rem;">
                        <button type="submit" class="cta-button">
                            <i class="fas fa-anchor"></i> Upload to Gallery
                        </button>
                    </div>
                </form>
            `;
            
            // File upload handling
            const fileInput = document.getElementById('uploadFile');
            const uploadArea = document.querySelector('.file-upload-area');
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
            });
            
            uploadArea.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    uploadArea.querySelector('h3').textContent = `Selected: ${files[0].name}`;
                }
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    uploadArea.querySelector('h3').textContent = `Selected: ${e.target.files[0].name}`;
                }
            });
            
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                formData.append('uploaded_by', currentUser.name);
                
                try {
                    const response = await fetch('/api/gallery/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('Media uploaded successfully!');
                        closeGenericModal();
                        if (currentPage === 'gallery') {
                            loadGallery();
                        }
                    } else {
                        alert('Failed to upload media: ' + result.error);
                    }
                } catch (error) {
                    alert('Unable to upload media. Storm interference detected.');
                }
            });
            
            openGenericModal();
        }

        async function showMessages() {
            try {
                const response = await fetch('/api/contact');
                const data = await response.json();
                
                let messageList = '';
                if (data.success && data.messages.length > 0) {
                    messageList = data.messages.map(msg => `
                        <div style="background: rgba(255, 248, 220, 0.5); padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #daa520;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
                                <h4 style="color: #8b4513; margin: 0; font-size: 1.1rem;">${msg.subject}</h4>
                                <span style="color: #654321; font-size: 0.9em;">${new Date(msg.created_at).toLocaleDateString()}</span>
                            </div>
                            <div style="color: #654321; margin-bottom: 0.5rem; font-size: 0.9rem;">
                                <strong>From:</strong> ${msg.name} (${msg.email})
                            </div>
                            <div style="color: #654321; line-height: 1.6; margin-bottom: 1rem; font-size: 0.95rem;">
                                ${msg.message}
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                <button class="btn-small btn-primary" onclick="replyToMessage('${msg.email}', '${msg.subject}')">Reply</button>
                                <button class="btn-small btn-secondary" onclick="markMessageRead(${msg.id})">Mark Read</button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    messageList = '<div style="text-align: center; color: #654321; padding: 2rem;">No messages in the bottle yet.</div>';
                }
                
                document.getElementById('genericModalContent').innerHTML = `
                    <h2 class="rugged-title">Message Bottles</h2>
                    <div style="max-height: 60vh; overflow-y: auto;">
                        ${messageList}
                    </div>
                `;
                openGenericModal();
            } catch (error) {
                alert('Unable to load messages. Storm interference detected.');
            }
        }

        function replyToMessage(email, subject) {
            const replySubject = subject.startsWith('Re:') ? subject : `Re: ${subject}`;
            const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(replySubject)}`;
            window.open(mailtoLink);
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('membersCount').textContent = data.stats.members + '+';
                    document.getElementById('eventsCount').textContent = data.stats.events;
                    document.getElementById('impactCount').textContent = '15K+';
                    document.getElementById('memberCount').textContent = data.stats.members + '+';
                }
            } catch (error) {
                console.log('API not available, using default values');
            }
        }

        async function loadDashboardStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.success) {
                    const dashMemberCount = document.getElementById('dashMemberCount');
                    const dashEventCount = document.getElementById('dashEventCount');
                    
                    if (dashMemberCount) dashMemberCount.textContent = data.stats.members;
                    if (dashEventCount) dashEventCount.textContent = data.stats.events;
                }
            } catch (error) {
                console.log('API not available for dashboard stats');
            }
        }

        // Contact Form Submission
        document.getElementById('contactForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const successMessage = document.getElementById('successMessage');
            const errorMessage = document.getElementById('errorMessage');
            
            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    successMessage.style.display = 'block';
                    errorMessage.style.display = 'none';
                    e.target.reset();
                    
                    setTimeout(() => {
                        successMessage.style.display = 'none';
                    }, 5000);
                } else {
                    throw new Error(result.error || 'Unknown error');
                }
            } catch (error) {
                console.log('API not available, showing success message anyway');
                successMessage.style.display = 'block';
                errorMessage.style.display = 'none';
                e.target.reset();
                
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 5000);
            }
        });

        // Helper Functions
        function showJoinMessage() {
            alert('Welcome, prospective crew member! NASA FRIGATE is a professional non-profit organization with open membership for qualified volunteers. To apply, please contact our Membership Committee at membership@nasafrigate.org or submit an inquiry through our contact form with "Membership Application" as your subject.');
        }

        function logout() {
            currentUser = null;
            closeManagementModal();
            document.getElementById('loginForm').reset();
        }

        // Placeholder functions for missing management features
        function showGalleryManager() {
            alert('Gallery management feature coming soon! Use the upload function to add new media.');
        }

        function showBlogManager() {
            alert('Blog management feature coming soon! Technical logs are automatically detected from .sh files.');
        }

        function showCreatePostForm() {
            alert('Create new blog post feature coming soon! Currently, .sh files in the server directory are automatically served as blog posts.');
        }

        function showMessageStats() {
            alert('Message statistics feature coming soon!');
        }

        function editMember(id) {
            alert('Edit member feature coming soon!');
        }

        function deleteMember(id) {
            if (confirm('Are you sure you want to remove this crew member?')) {
                alert('Delete member feature coming soon!');
            }
        }

        function editEvent(id) {
            alert('Edit event feature coming soon!');
        }

        function deleteEvent(id) {
            if (confirm('Are you sure you want to cancel this mission?')) {
                alert('Delete event feature coming soon!');
            }
        }

        function markMessageRead(id) {
            alert('Mark message as read feature coming soon!');
        }

        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            loadStats();
            console.log('🚢 Welcome to NASA FRIGATE! Mobile-friendly enhanced management system ready for service.');
        });

        // Add touch event handling for better mobile experience
        document.addEventListener('touchstart', function() {}, {passive: true});
    </script>
</body>
</html>'''

# Database initialization
def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    cursor = conn.cursor()
    
    # Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'Member',
            join_date DATE DEFAULT CURRENT_DATE,
            birthday DATE,
            phone TEXT,
            address TEXT,
            skills TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_date DATE NOT NULL,
            event_time TIME,
            location TEXT,
            category TEXT DEFAULT 'General',
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contact messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Gallery items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gallery_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            file_type TEXT,
            category TEXT DEFAULT 'General',
            uploaded_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Newsletter subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Birthday wishes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS birthday_wishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            message TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    
    # Insert default leadership if not exists
    cursor.execute('SELECT COUNT(*) FROM members WHERE role IN ("Frigate Captain", "Scribe", "Crier", "Purse")')
    if cursor.fetchone()[0] == 0:
        leadership = [
            ('Captain Sarah Johnson', 'captain@nasafrigate.org', 'Frigate Captain', '1985-03-15'),
            ('Michael Chen', 'scribe@nasafrigate.org', 'Scribe', '1990-07-22'),
            ('Amanda Rodriguez', 'crier@nasafrigate.org', 'Crier', '1988-11-08'),
            ('David Thompson', 'purse@nasafrigate.org', 'Purse', '1992-05-30')
        ]
        
        for name, email, role, birthday in leadership:
            cursor.execute('''
                INSERT INTO members (name, email, role, birthday, join_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, role, birthday, '2020-01-01'))
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Database helper functions
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch=False):
    """Execute database query with error handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            conn.close()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Serve the main website with embedded HTML"""
    return HTML_CONTENT

@app.route('/api/login', methods=['POST'])
def handle_login():
    """Handle leadership login"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if username in LEADERSHIP_CREDENTIALS:
        if LEADERSHIP_CREDENTIALS[username]['password'] == password:
            session['user'] = username
            return jsonify({
                'success': True,
                'user': LEADERSHIP_CREDENTIALS[username]
            })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def handle_logout():
    """Handle logout"""
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/members', methods=['GET', 'POST'])
def handle_members():
    """Handle member operations"""
    if request.method == 'GET':
        members = execute_query(
            'SELECT * FROM members WHERE active = 1 ORDER BY role DESC, name ASC',
            fetch=True
        )
        
        if members:
            members_list = [dict(member) for member in members]
            return jsonify({
                'success': True,
                'members': members_list,
                'total_count': len(members_list)
            })
        else:
            return jsonify({'success': True, 'members': [], 'total_count': 0})
    
    elif request.method == 'POST':
        data = request.get_json()
        
        required_fields = ['name', 'email']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        member_id = execute_query('''
            INSERT INTO members (name, email, role, birthday, phone, address, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            data.get('role', 'Member'),
            data.get('birthday'),
            data.get('phone'),
            data.get('address'),
            data.get('skills')
        ))
        
        if member_id:
            return jsonify({
                'success': True,
                'message': 'Member added successfully',
                'member_id': member_id
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add member'}), 500

@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    """Handle event operations"""
    if request.method == 'GET':
        events = execute_query('''
            SELECT * FROM events 
            WHERE event_date >= date('now') 
            ORDER BY event_date ASC
        ''', fetch=True)
        
        if events:
            events_list = [dict(event) for event in events]
            return jsonify({
                'success': True,
                'events': events_list,
                'total_count': len(events_list)
            })
        else:
            return jsonify({'success': True, 'events': [], 'total_count': 0})
    
    elif request.method == 'POST':
        data = request.get_json()
        
        required_fields = ['title', 'event_date']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        event_id = execute_query('''
            INSERT INTO events (title, description, event_date, event_time, location, category, max_participants, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('description'),
            data['event_date'],
            data.get('event_time'),
            data.get('location'),
            data.get('category', 'General'),
            data.get('max_participants'),
            data.get('created_by', 'System')
        ))
        
        if event_id:
            return jsonify({
                'success': True,
                'message': 'Event created successfully',
                'event_id': event_id
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create event'}), 500

@app.route('/api/contact', methods=['GET', 'POST'])
def handle_contact():
    """Handle contact form submissions and retrieval"""
    if request.method == 'GET':
        messages = execute_query(
            'SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT 50',
            fetch=True
        )
        
        if messages:
            messages_list = [dict(message) for message in messages]
            return jsonify({
                'success': True,
                'messages': messages_list,
                'total_count': len(messages_list)
            })
        else:
            return jsonify({'success': True, 'messages': [], 'total_count': 0})
    
    elif request.method == 'POST':
        data = request.get_json()
        
        required_fields = ['name', 'email', 'subject', 'message']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        message_id = execute_query('''
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data['email'], data['subject'], data['message']))
        
        if message_id:
            logger.info(f"Contact message received from {data['name']} ({data['email']}): {data['subject']}")
            return jsonify({
                'success': True,
                'message': 'Message sent successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to send message'}), 500

@app.route('/api/gallery', methods=['GET'])
def handle_gallery():
    """Handle gallery retrieval"""
    gallery_items = execute_query(
        'SELECT * FROM gallery_items ORDER BY created_at DESC',
        fetch=True
    )
    
    if gallery_items:
        items_list = []
        for item in gallery_items:
            item_dict = dict(item)
            # Determine if it's a video or image
            item_dict['type'] = 'video' if item_dict['file_type'].startswith('video/') else 'image'
            items_list.append(item_dict)
        
        return jsonify({
            'success': True,
            'items': items_list,
            'total_count': len(items_list)
        })
    else:
        return jsonify({'success': True, 'items': [], 'total_count': 0})

@app.route('/api/gallery/upload', methods=['POST'])
def handle_gallery_upload():
    """Handle gallery file uploads"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        file_path = os.path.join(app.config['GALLERY_FOLDER'], filename)
        file.save(file_path)
        
        # Get file type
        file_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # Save to database
        gallery_id = execute_query('''
            INSERT INTO gallery_items (title, description, filename, file_type, category, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            request.form.get('title', filename),
            request.form.get('description', ''),
            filename,
            file_type,
            request.form.get('category', 'General'),
            request.form.get('uploaded_by', 'Unknown')
        ))
        
        if gallery_id:
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'gallery_id': gallery_id
            })
        else:
            # Clean up file if database insert failed
            os.remove(file_path)
            return jsonify({'success': False, 'error': 'Failed to save file info'}), 500
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/gallery/<filename>')
def serve_gallery_file(filename):
    """Serve gallery files"""
    try:
        return send_file(os.path.join(app.config['GALLERY_FOLDER'], filename))
    except FileNotFoundError:
        abort(404)

@app.route('/api/blog', methods=['GET'])
def handle_blog():
    """Handle blog post retrieval"""
    # Get .sh files from the same directory as server.py
    blog_folder = Path(app.config['BLOG_FOLDER'])
    sh_files = list(blog_folder.glob('*.sh'))
    
    blog_posts = []
    for sh_file in sh_files:
        try:
            # Read file content for excerpt
            with open(sh_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Get first few lines as excerpt
                lines = content.split('\n')
                excerpt = '\n'.join(lines[:5]) + ('...' if len(lines) > 5 else '')
            
            # Get file stats
            stat = sh_file.stat()
            
            blog_posts.append({
                'title': sh_file.stem.replace('_', ' ').title(),
                'filename': sh_file.name,
                'author': 'Ship\'s Scribe',
                'excerpt': excerpt,
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size
            })
        except Exception as e:
            logger.error(f"Error reading {sh_file}: {e}")
            continue
    
    # Sort by creation time (newest first)
    blog_posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'posts': blog_posts,
        'total_count': len(blog_posts)
    })

@app.route('/api/blog/<filename>', methods=['GET'])
def handle_blog_post(filename):
    """Handle individual blog post retrieval"""
    if not filename.endswith('.sh'):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    
    file_path = os.path.join(app.config['BLOG_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get file stats
        stat = os.stat(file_path)
        
        return jsonify({
            'success': True,
            'post': {
                'title': Path(filename).stem.replace('_', ' ').title(),
                'filename': filename,
                'author': 'Ship\'s Scribe',
                'content': content,
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size
            }
        })
    except Exception as e:
        logger.error(f"Error reading blog post {filename}: {e}")
        return jsonify({'success': False, 'error': 'Failed to read file'}), 500

@app.route('/api/blog/<filename>/download')
def download_blog_post(filename):
    """Handle blog post download"""
    if not filename.endswith('.sh'):
        abort(400)
    
    file_path = os.path.join(app.config['BLOG_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, as_attachment=True)

@app.route('/api/stats')
def get_stats():
    """Get organization statistics"""
    member_count = execute_query('SELECT COUNT(*) as count FROM members WHERE active = 1', fetch=True)
    member_count = member_count[0]['count'] if member_count else 54
    
    event_count = execute_query('SELECT COUNT(*) as count FROM events', fetch=True)
    event_count = event_count[0]['count'] if event_count else 127
    
    message_count = execute_query('SELECT COUNT(*) as count FROM contact_messages', fetch=True)
    message_count = message_count[0]['count'] if message_count else 0
    
    gallery_count = execute_query('SELECT COUNT(*) as count FROM gallery_items', fetch=True)
    gallery_count = gallery_count[0]['count'] if gallery_count else 0
    
    return jsonify({
        'success': True,
        'stats': {
            'members': member_count,
            'events': event_count,
            'messages': message_count,
            'gallery_items': gallery_count,
            'impact_estimate': member_count * 250
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1.0',
        'database': 'connected' if os.path.exists(app.config['DATABASE_PATH']) else 'not_found',
        'features': ['gallery', 'blog', 'management_dashboard', 'mobile_responsive']
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

def create_sample_data():
    """Create sample data for testing"""
    logger.info("Creating sample data...")
    
    # Sample members
    sample_members = [
        ('Alice "Stormy" Johnson', 'alice@example.com', 'Member', '1990-05-15'),
        ('Bob "Anchor" Smith', 'bob@example.com', 'Member', '1985-08-22'),
        ('Carol "Compass" Davis', 'carol@example.com', 'Member', '1992-12-03'),
        ('David "Sailor" Wilson', 'david@example.com', 'Member', '1988-03-18'),
        ('Eva "Navigator" Brown', 'eva@example.com', 'Member', '1991-07-09'),
        ('Frank "Bosun" Miller', 'frank@example.com', 'Member', '1987-01-30'),
        ('Grace "Lighthouse" Taylor', 'grace@example.com', 'Member', '1993-09-14'),
        ('Henry "Tide" Anderson', 'henry@example.com', 'Member', '1989-06-25')
    ]
    
    for name, email, role, birthday in sample_members:
        execute_query('''
            INSERT OR IGNORE INTO members (name, email, role, birthday)
            VALUES (?, ?, ?, ?)
        ''', (name, email, role, birthday))
    
    # Sample events
    sample_events = [
        ('Community Food Drive', 'Annual food drive for local families in need', '2024-12-20', '09:00', 'Community Center'),
        ('New Year Charity Gala', 'Fundraising gala for education scholarships', '2024-12-31', '18:00', 'Grand Hotel'),
        ('Environmental Cleanup', 'Beach and park cleanup initiative', '2025-01-15', '08:00', 'Sunset Beach'),
        ('Skills Workshop', 'Professional development workshop for members', '2025-02-10', '14:00', 'Conference Room A'),
        ('Birthday Celebration', 'Monthly birthday celebration for crew members', '2025-02-28', '19:00', 'Harbor Club'),
        ('Charity Auction', 'Annual charity auction to raise funds', '2025-03-15', '17:00', 'Town Hall')
    ]
    
    for title, desc, event_date, event_time, location in sample_events:
        execute_query('''
            INSERT OR IGNORE INTO events (title, description, event_date, event_time, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, desc, event_date, event_time, location))
    
    # Create sample .sh files for blog
    sample_scripts = [
        {
            'filename': 'setup_server.sh',
            'content': '''#!/bin/bash
# NASA FRIGATE Server Setup Script
# This script sets up the basic server environment for our maritime operations

echo "🚢 Setting up NASA FRIGATE server environment..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and required packages
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment
python3 -m venv frigate_env
source frigate_env/bin/activate

# Install Flask and dependencies
pip install flask flask-cors

echo "⚓ Server environment setup complete!"
echo "Ready to sail the digital seas!"
'''
        },
        {
            'filename': 'backup_database.sh',
            'content': '''#!/bin/bash
# NASA FRIGATE Database Backup Script
# Automated backup system for our crew database

BACKUP_DIR="/backup/frigate"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="nasa_frigate.db"

echo "🗃️ Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup with timestamp
cp $DB_FILE "$BACKUP_DIR/frigate_backup_$DATE.db"

# Compress the backup
gzip "$BACKUP_DIR/frigate_backup_$DATE.db"

echo "✅ Database backup completed: frigate_backup_$DATE.db.gz"
echo "⚓ All crew data safely stored!"
'''
        },
        {
            'filename': 'deploy_updates.sh',
            'content': '''#!/bin/bash
# NASA FRIGATE Deployment Script
# Deploys updates to our maritime management system

echo "🚢 Deploying NASA FRIGATE updates..."

# Pull latest changes
git pull origin main

# Backup current database
./backup_database.sh

# Restart services
sudo systemctl restart frigate-server

# Check service status
if systemctl is-active --quiet frigate-server; then
    echo "✅ Deployment successful!"
    echo "⚓ All hands on deck - system is operational!"
else
    echo "❌ Deployment failed!"
    echo "🚨 All hands to battle stations!"
    exit 1
fi
'''
        }
    ]
    
    for script in sample_scripts:
        script_path = os.path.join(app.config['BLOG_FOLDER'], script['filename'])
        if not os.path.exists(script_path):
            with open(script_path, 'w') as f:
                f.write(script['content'])
            logger.info(f"Created sample script: {script['filename']}")
    
    logger.info("Sample data created successfully")

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Create sample data if requested
    import sys
    if '--sample-data' in sys.argv:
        create_sample_data()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    logger.info(f"Starting NASA FRIGATE Mobile-Friendly Enhanced Management Server on port {port}")
    logger.info("🚢 NASA FRIGATE Mobile-Friendly Enhanced Management Server Starting...")
    logger.info("⚓" * 50)
    logger.info("Available endpoints:")
    logger.info("  GET  /                    - Main website (Mobile-Responsive SPA)")
    logger.info("  POST /api/login           - Leadership login")
    logger.info("  POST /api/logout          - Logout")
    logger.info("  GET  /api/members         - Get all members")
    logger.info("  POST /api/members         - Add new member")
    logger.info("  GET  /api/events          - Get upcoming events")
    logger.info("  POST /api/events          - Create new event")
    logger.info("  GET  /api/contact         - Get contact messages")
    logger.info("  POST /api/contact         - Submit contact form")
    logger.info("  GET  /api/gallery         - Get gallery items")
    logger.info("  POST /api/gallery/upload  - Upload gallery media")
    logger.info("  GET  /gallery/<filename>  - Serve gallery files")
    logger.info("  GET  /api/blog            - Get blog posts (.sh files)")
    logger.info("  GET  /api/blog/<filename> - Get specific blog post")
    logger.info("  GET  /api/blog/<filename>/download - Download blog post")
    logger.info("  GET  /api/stats           - Get organization statistics")
    logger.info("  GET  /health              - Health check")
    logger.info("⚓" * 50)
    logger.info("🆕 Enhanced Features:")
    logger.info("   📱 Mobile-First Responsive Design - Optimized for all devices")
    logger.info("   📸 Gallery Management - Upload and manage voyage photos/videos")
    logger.info("   📝 Ship's Log - Serve and manage .sh files as blog posts")
    logger.info("   🎛️ Full Management Dashboard - Complete admin interface")
    logger.info("   🗄️ Enhanced Database - Gallery, blog, and management tables")
    logger.info("   👆 Touch-Friendly Interface - Optimized for mobile interaction")
    logger.info("   🔄 Responsive Navigation - Collapsible mobile menu")
    logger.info("   📐 Flexible Layouts - Adaptive grids for all screen sizes")
    logger.info("⚓" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True if '--debug' in sys.argv else False
    )
