import { Link } from "react-router-dom";
import bgLogin from "../assets/bg_login.png";
import gtsLogo from "../assets/gabani_logo.png";
import SeoHead from "../components/SeoHead";

const SUPPORT_EMAIL = "support@gtslogistics.com";
const SUPPORT_PHONE = "+1 (778) 651-8297";
const SUPPORT_PHONE_HREF = "tel:+17786518297";

export default function PublicSupport() {
  return (
    <div
      className="min-h-screen bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${bgLogin})` }}
    >
      <SeoHead
        title="Support - GTS Logistics"
        description="Contact GTS Logistics support for platform access, billing help, and logistics assistance."
        keywords="gts support, logistics support, freight support, load board help"
        canonical="https://www.gtsdispatcher.com/support"
        ogTitle="GTS Logistics Support"
        ogDescription="Reach GTS Logistics support for platform access, billing, and operational help."
        ogUrl="https://www.gtsdispatcher.com/support"
        twitterTitle="GTS Logistics Support"
        twitterDescription="Reach GTS Logistics support for platform access, billing, and operational help."
      />
      <div className="min-h-screen bg-black/70">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <Link to="/">
              <img src={gtsLogo} alt="GTS Logistics" className="h-12" />
            </Link>
            <div className="flex gap-3">
              <Link
                to="/contact"
                className="rounded border border-white px-5 py-2 text-sm text-white transition hover:bg-white/10"
              >
                Contact Us
              </Link>
              <Link
                to="/login"
                className="rounded bg-red-600 px-5 py-2 text-sm text-white transition hover:bg-red-700"
              >
                Log In
              </Link>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-16">
          <div className="mx-auto max-w-4xl rounded-3xl border border-white/15 bg-black/40 p-8 backdrop-blur-sm">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-white">GTS Logistics Support</h1>
              <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-300">
                Reach our support team for account access, billing questions, and logistics platform assistance.
              </p>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              <Link
                to="/contact"
                className="rounded-2xl border border-white/10 bg-white/5 p-6 transition hover:border-red-500/40 hover:bg-white/10"
              >
                <h2 className="text-xl font-semibold text-white">Contact Form</h2>
                <p className="mt-2 text-sm text-gray-300">
                  Send a message to our team and receive a response through the public contact page.
                </p>
              </Link>

              <a
                href={`mailto:${SUPPORT_EMAIL}`}
                className="rounded-2xl border border-white/10 bg-white/5 p-6 transition hover:border-red-500/40 hover:bg-white/10"
              >
                <h2 className="text-xl font-semibold text-white">Email Support</h2>
                <p className="mt-2 text-sm text-gray-300">{SUPPORT_EMAIL}</p>
              </a>

              <a
                href={SUPPORT_PHONE_HREF}
                className="rounded-2xl border border-white/10 bg-white/5 p-6 transition hover:border-red-500/40 hover:bg-white/10"
              >
                <h2 className="text-xl font-semibold text-white">Call Support</h2>
                <p className="mt-2 text-sm text-gray-300">{SUPPORT_PHONE}</p>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
