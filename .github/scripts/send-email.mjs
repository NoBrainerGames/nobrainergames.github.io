import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  service: 'Gmail',
  host: 'smtp.gmail.com',
  port: 465,
  secure: true,
  auth: {
    user: process.env.GMAIL_APP_USER,
    pass: process.env.GMAIL_APP_PASSWORD,
  },
});

(async () => {
  try {
    await transporter.sendMail({
      from: `"Contact Referrer" <${process.env.GMAIL_APP_USER}>`,
      to: "contact@nobrainergames.com",
      subject: 'New email address received',
      html: process.env.CONTACT_EMAIL,
    });
  } catch (error) {
    console.error(error);
  }
})();
