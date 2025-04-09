import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/legal.css';

const PrivacyPage = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <h1>Privacy Policy</h1>
        <div className="legal-content">
          <div className="last-updated">Last Updated: {new Date().toLocaleDateString()}</div>
          
          <section>
            <h2>1. Introduction</h2>
            <p>
              At Financial Analysis Platform, we respect your privacy and are committed to protecting your personal data.
              This Privacy Policy explains how we collect, use, process, and store your information when you use our platform.
            </p>
          </section>
          
          <section>
            <h2>2. Information We Collect</h2>
            <p>We collect several types of information from and about users of our platform, including:</p>
            <ul>
              <li><strong>Personal Information:</strong> Email address, name, phone number, and other contact details you provide when registering or updating your profile.</li>
              <li><strong>Account Information:</strong> Login credentials, account preferences, and settings.</li>
              <li><strong>Financial Data:</strong> Watchlists, stock interaction history, and other financial information you create or provide while using our services.</li>
              <li><strong>Usage Data:</strong> Information about how you use our platform, including page views, clicks, and time spent on the platform.</li>
              <li><strong>Technical Data:</strong> IP address, browser type and version, device information, and cookies.</li>
            </ul>
          </section>
          
          <section>
            <h2>3. How We Use Your Information</h2>
            <p>We use the information we collect for various purposes, including to:</p>
            <ul>
              <li>Provide, maintain, and improve our services</li>
              <li>Process transactions and manage your account</li>
              <li>Personalize your experience and deliver content relevant to your interests</li>
              <li>Communicate with you about updates, security alerts, and support</li>
              <li>Analyze usage patterns and optimize our platform</li>
              <li>Protect against fraudulent, unauthorized, or illegal activity</li>
            </ul>
          </section>
          
          <section>
            <h2>4. Data Security</h2>
            <p>
              We implement appropriate technical and organizational measures to protect your personal information.
              However, no method of transmission over the Internet or electronic storage is 100% secure.
              While we strive to use commercially acceptable means to protect your personal data,
              we cannot guarantee its absolute security.
            </p>
          </section>
          
          <section>
            <h2>5. Data Retention</h2>
            <p>
              We retain your personal information for as long as necessary to fulfill the purposes outlined in this
              Privacy Policy, unless a longer retention period is required or permitted by law.
            </p>
          </section>
          
          <section>
            <h2>6. Your Rights</h2>
            <p>Depending on your location, you may have certain rights regarding your personal data, including:</p>
            <ul>
              <li>The right to access personal information we hold about you</li>
              <li>The right to request correction of inaccurate data</li>
              <li>The right to request deletion of your data</li>
              <li>The right to restrict or object to processing</li>
              <li>The right to data portability</li>
              <li>The right to withdraw consent</li>
            </ul>
            <p>
              To exercise any of these rights, please contact us using the information provided in the "Contact Us" section.
            </p>
          </section>
          
          <section>
            <h2>7. Cookies and Similar Technologies</h2>
            <p>
              We use cookies and similar tracking technologies to track activity on our platform and to hold certain information.
              You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent.
            </p>
          </section>
          
          <section>
            <h2>8. Third-Party Services</h2>
            <p>
              Our platform may contain links to third-party websites or services that are not owned or controlled by us.
              We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party sites or services.
            </p>
          </section>
          
          <section>
            <h2>9. Changes to This Privacy Policy</h2>
            <p>
              We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page
              and updating the "Last Updated" date at the top of this policy.
            </p>
          </section>
          
          <section>
            <h2>10. Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy, please contact us at:
            </p>
            <p className="contact-info">
              Financial Analysis Platform<br />
              Email: privacy@financialanalysisplatform.com<br />
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

export default PrivacyPage;
