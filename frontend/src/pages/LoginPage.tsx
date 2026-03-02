// EVA-STORY: ACA-04-007
/**
 * LoginPage -- Multi-tenant sign-in via MSAL.js
 * Authority: https://login.microsoftonline.com/common (any Microsoft account)
 * Flow: Sign-in -> Extract tokens -> POST /v1/auth/preflight -> Redirect to /connect-subscription
 */
import React, { useEffect } from 'react';
import { useMsal } from '@azure/msal-react';
import { PrimaryButton, Stack, Text, Spinner } from '@fluentui/react';
import { useNavigate } from 'react-router-dom';

export const LoginPage: React.FC = () => {
  const { instance, accounts } = useMsal();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = React.useState(false);

  useEffect(() => {
    // If already signed in, redirect to connect-subscription
    if (accounts.length > 0) {
      navigate('/connect-subscription');
    }
  }, [accounts, navigate]);

  const handleSignIn = async () => {
    setIsLoading(true);
    try {
      // Initiate sign-in with common authority (multi-tenant)
      const response = await instance.loginPopup({
        scopes: ['https://management.azure.com/.default'],
        authority: 'https://login.microsoftonline.com/common',
      });

      // Store tokens in session
      sessionStorage.setItem('accessToken', response.accessToken);
      if (response.expiresOn) {
        sessionStorage.setItem('expiresOn', response.expiresOn.toString());
      }

      // Call /v1/auth/preflight to validate permissions
      const preflightResponse = await fetch(
        `${process.env.REACT_APP_API_URL}/v1/auth/preflight`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${response.accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (preflightResponse.ok) {
        // Preflight passed -- redirect to connect-subscription
        navigate('/connect-subscription');
      } else {
        // Preflight failed -- show error
        const error = await preflightResponse.json();
        console.error('[FAIL] Preflight error:', error);
      }
    } catch (err) {
      console.error('[FAIL] Sign-in error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Stack
      horizontalAlign="center"
      verticalAlign="center"
      styles={{ root: { minHeight: '100vh', padding: '20px' } }}
    >
      <Stack
        styles={{
          root: {
            width: '100%',
            maxWidth: '400px',
            padding: '40px',
            border: '1px solid #e1e1e1',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          },
        }}
      >
        <Text
          variant="xxLarge"
          styles={{ root: { marginBottom: '24px', fontWeight: 600 } }}
        >
          Azure Cost Advisor
        </Text>

        <Text
          variant="medium"
          styles={{ root: { marginBottom: '32px', color: '#666' } }}
        >
          Sign in with your Microsoft account to connect your Azure subscription
        </Text>

        {isLoading ? (
          <Stack horizontalAlign="center">
            <Spinner label="Signing in..." />
          </Stack>
        ) : (
          <PrimaryButton
            text="Sign in with Microsoft"
            onClick={handleSignIn}
            styles={{ root: { minHeight: '44px', fontSize: '16px' } }}
          />
        )}

        <Text
          variant="small"
          styles={{
            root: {
              marginTop: '24px',
              color: '#999',
              textAlign: 'center',
            },
          }}
        >
          We connect to your Azure subscription to analyze costs and opportunities.
        </Text>
      </Stack>
    </Stack>
  );
};
