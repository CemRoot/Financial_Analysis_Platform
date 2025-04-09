import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/legal.css';

const TermsPage = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Terms and Conditions</h1>
        <div className="legal-content">
          <div className="last-updated">Last Updated: {new Date().toLocaleDateString()}</div>
          
          <section>
            <h2>1. Introduction</h2>
            <p>
              Welcome to Financial Analysis Platform. These Terms and Conditions govern your use of our 
              website and services. By accessing or using our platform, you agree to be bound by these Terms. 
              If you disagree with any part of these terms, you may not access our services.
            </p>
          </section>
          
          <section>
            <h2>2. Account Registration</h2>
            <p>
              When you create an account with us, you must provide accurate, complete, and up-to-date information. 
              You are responsible for safeguarding the password and for all activities that occur under your account. 
              Notify us immediately of any unauthorized use of your account.
            </p>
          </section>
          
          <section>
            <h2>3. Financial Data and Investment Information</h2>
            <p>
              The financial information presented on our platform is for informational and educational purposes only. 
              It is not intended as investment advice. We make no representations or warranties regarding the accuracy, 
              completeness, or timeliness of the data presented.
            </p>
            <p>
              Past performance is not indicative of future results. All investments involve risk, including the 
              possible loss of principal. You should conduct your own research and consult with a qualified financial 
              advisor before making any investment decisions.
            </p>
          </section>
          
          <section>
            <h2>4. User Conduct</h2>
            <p>
              You agree not to misuse our services or assist anyone in misusing our services for any illegal, 
              harmful, or disruptive purposes. You specifically agree not to:
            </p>
            <ul>
              <li>Use the services to harm, threaten, or harass another person, organization, or Financial Analysis Platform</li>
              <li>Damage, disable, overburden, or impair any aspect of our services</li>
              <li>Access or attempt to access other users' accounts</li>
              <li>Violate any applicable laws or regulations</li>
              <li>Infringe upon intellectual property rights of others</li>
            </ul>
          </section>
          
          <section>
            <h2>5. Data Privacy</h2>
            <p>
              Your privacy is important to us. Our <Link to="/privacy">Privacy Policy</Link> outlines how we collect, 
              use, and protect your personal information. By using our platform, you consent to the data practices 
              described in our Privacy Policy.
            </p>
          </section>
          
          <section>
            <h2>6. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by law, Financial Analysis Platform shall not be liable for any indirect, 
              incidental, special, consequential, or punitive damages, including without limitation, loss of profits or 
              data, arising out of or related to your use of our services.
            </p>
          </section>
          
          <section>
            <h2>7. Changes to Terms</h2>
            <p>
              We reserve the right to modify these terms at any time. We will provide notice of significant changes by 
              posting the new Terms on our platform. Your continued use of our services after such changes constitutes 
              your acceptance of the new Terms.
            </p>
          </section>
          
          <section>
            <h2>8. Termination</h2>
            <p>
              We may terminate or suspend access to our services immediately, without prior notice or liability, for 
              any reason, including without limitation if you breach the Terms.
            </p>
          </section>
          
          <section>
            <h2>9. Contact Us</h2>
            <p>
              If you have any questions about these Terms, please contact us at:
            </p>
            <p className="contact-info">
              Financial Analysis Platform<br />
              Email: support@financialanalysisplatform.com<br />
              Phone: (123) 456-7890
            </p>
          </section>
        </div>
        
        <div className="legal-footer">
          <Link to="/" className="back-button">Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default TermsPage;
