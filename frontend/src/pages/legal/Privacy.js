import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../../styles/legal.css';

const Privacy = () => {
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
        
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last updated: July 1, 2023</p>
        
        <section>
          <h2>1. Introduction</h2>
          <p>
            At Financial Analysis Platform, we respect your privacy and are committed to protecting your personal data. 
            This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website 
            and services. Please read this Privacy Policy carefully.
          </p>
        </section>
        
        <section>
          <h2>2. Information We Collect</h2>
          <p>We may collect the following types of information:</p>
          
          <h3>2.1 Personal Data</h3>
          <p>
            When you register for an account, we collect personal information such as your name, email address, 
            and other contact details. We may also collect information about your financial preferences and interests 
            to personalize your experience.
          </p>
          
          <h3>2.2 Usage Data</h3>
          <p>
            We automatically collect information about how you interact with our Platform, including the pages you visit, 
            the time and duration of your visits, your IP address, browser type, and operating system.
          </p>
          
          <h3>2.3 Cookies and Tracking Technologies</h3>
          <p>
            We use cookies and similar tracking technologies to track activity on our Platform and to store certain information. 
            Cookies are files with a small amount of data which may include an anonymous unique identifier. 
            You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, 
            if you do not accept cookies, you may not be able to use some portions of our Platform.
          </p>
        </section>
        
        <section>
          <h2>3. How We Use Your Information</h2>
          <p>We use the information we collect for various purposes, including to:</p>
          <ul>
            <li>Provide, maintain, and improve our services</li>
            <li>Process transactions and send related information</li>
            <li>Send administrative information, such as updates, security alerts, and support messages</li>
            <li>Respond to your comments, questions, and requests</li>
            <li>Personalize your experience and deliver content tailored to your interests</li>
            <li>Monitor usage patterns to improve our Platform and services</li>
            <li>Protect against, identify, and prevent fraud and other illegal activities</li>
          </ul>
        </section>
        
        <section>
          <h2>4. How We Share Your Information</h2>
          <p>
            We may share your information with third parties in the following situations:
          </p>
          <ul>
            <li>With service providers that perform services on our behalf</li>
            <li>To comply with legal obligations</li>
            <li>To protect and defend our rights and property</li>
            <li>With your consent or at your direction</li>
          </ul>
          <p>
            We do not sell your personal information to third parties.
          </p>
        </section>
        
        <section>
          <h2>5. Data Security</h2>
          <p>
            We implement appropriate technical and organizational measures to protect the security of your personal information. 
            However, please note that no method of transmission over the Internet or electronic storage is 100% secure. 
            While we strive to use commercially acceptable means to protect your personal information, we cannot guarantee 
            its absolute security.
          </p>
        </section>
        
        <section>
          <h2>6. Your Data Protection Rights</h2>
          <p>
            Depending on your location, you may have certain rights regarding your personal information, such as:
          </p>
          <ul>
            <li>The right to access information we hold about you</li>
            <li>The right to request correction of inaccurate personal information</li>
            <li>The right to request deletion of your personal information</li>
            <li>The right to restrict or object to processing of your personal information</li>
            <li>The right to data portability</li>
          </ul>
          <p>
            To exercise any of these rights, please contact us using the information provided in the "Contact Us" section.
          </p>
        </section>
        
        <section>
          <h2>7. Children's Privacy</h2>
          <p>
            Our Platform is not intended for use by children under the age of 18. We do not knowingly collect personal information 
            from children under 18. If we learn that we have collected personal information from a child under 18, 
            we will take steps to delete such information as soon as possible.
          </p>
        </section>
        
        <section>
          <h2>8. Changes to This Privacy Policy</h2>
          <p>
            We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy 
            on this page and updating the "Last updated" date. You are advised to review this Privacy Policy periodically for any changes.
          </p>
        </section>
        
        <section>
          <h2>9. Contact Us</h2>
          <p>
            If you have any questions about this Privacy Policy, please contact us at privacy@financialanalysisplatform.com.
          </p>
        </section>
        
        <div className="legal-navigation">
          <Link to="/auth" className="back-button">Back to Login</Link>
          <Link to="/terms" className="related-link">View Terms of Service</Link>
        </div>
      </div>
    </div>
  );
};

export default Privacy; 