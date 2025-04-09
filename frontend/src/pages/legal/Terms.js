import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../../styles/legal.css';

const Terms = () => {
  const navigate = useNavigate();
  
  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <div className="legal-page">
      <div className="legal-container">
        <div className="top-navigation">
          <button onClick={handleGoBack} className="back-button-top">
            &larr; Back
          </button>
        </div>
        
        <h1>Terms of Service</h1>
        <p className="last-updated">Last updated: July 1, 2023</p>
        
        <section>
          <h2>1. Introduction</h2>
          <p>
            Welcome to the Financial Analysis Platform. By using our website and services, you agree to comply 
            with and be bound by the following terms and conditions. Please review these terms carefully.
          </p>
        </section>
        
        <section>
          <h2>2. Definitions</h2>
          <p>
            <strong>"Platform"</strong> refers to the Financial Analysis Platform website and services.<br />
            <strong>"User"</strong> refers to any individual or entity that accesses or uses the Platform.<br />
            <strong>"Content"</strong> refers to all information, data, text, software, music, sound, photographs, 
            graphics, video, messages, or other materials that are posted, generated, provided or otherwise made 
            available through the Platform.
          </p>
        </section>
        
        <section>
          <h2>3. Account Registration</h2>
          <p>
            To access certain features of the Platform, you may be required to register for an account. 
            When you register, you agree to provide accurate, current, and complete information about yourself 
            and to update such information as necessary. You are responsible for maintaining the confidentiality 
            of your account credentials and for all activities that occur under your account.
          </p>
        </section>
        
        <section>
          <h2>4. Financial Data and Information</h2>
          <p>
            Our Platform provides financial data and analytics for informational purposes only. This information 
            should not be considered as financial advice or recommendation to buy or sell any security or investment. 
            We do not guarantee the accuracy, completeness, or timeliness of the information provided. You should 
            consult with a qualified financial advisor before making any investment decisions.
          </p>
        </section>
        
        <section>
          <h2>5. Use of Services</h2>
          <p>
            You agree to use the Platform only for lawful purposes and in accordance with these Terms. You agree not to:
          </p>
          <ul>
            <li>Use the Platform in any way that violates any applicable local, state, national, or international law or regulation</li>
            <li>Use the Platform to engage in any conduct that restricts or inhibits anyone's use or enjoyment of the Platform</li>
            <li>Attempt to gain unauthorized access to any portion of the Platform</li>
            <li>Use the Platform to transmit or upload any viruses, malware, or other malicious code</li>
            <li>Collect or harvest any information from the Platform, including user information, without authorization</li>
          </ul>
        </section>
        
        <section>
          <h2>6. Intellectual Property</h2>
          <p>
            The Platform and its original content, features, and functionality are owned by the Financial Analysis Platform 
            and are protected by international copyright, trademark, patent, trade secret, and other intellectual property 
            or proprietary rights laws.
          </p>
        </section>
        
        <section>
          <h2>7. Limitation of Liability</h2>
          <p>
            In no event shall the Financial Analysis Platform, its directors, employees, partners, agents, suppliers, 
            or affiliates be liable for any indirect, incidental, special, consequential, or punitive damages, including 
            without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your 
            access to or use of or inability to access or use the Platform.
          </p>
        </section>
        
        <section>
          <h2>8. Changes to Terms</h2>
          <p>
            We reserve the right to modify these Terms at any time. We will notify you of any changes by posting the 
            new Terms on the Platform. Your continued use of the Platform after such modifications will constitute your 
            acknowledgment of the modified Terms and agreement to abide and be bound by the modified Terms.
          </p>
        </section>
        
        <section>
          <h2>9. Governing Law</h2>
          <p>
            These Terms shall be governed by and construed in accordance with the laws of the United States, 
            without regard to its conflict of law provisions.
          </p>
        </section>
        
        <section>
          <h2>10. Contact Us</h2>
          <p>
            If you have any questions about these Terms, please contact us at support@financialanalysisplatform.com.
          </p>
        </section>
        
        <div className="legal-navigation">
          <Link to="/auth" className="back-button">Back to Login</Link>
          <Link to="/privacy" className="related-link">View Privacy Policy</Link>
        </div>
      </div>
    </div>
  );
};

export default Terms; 