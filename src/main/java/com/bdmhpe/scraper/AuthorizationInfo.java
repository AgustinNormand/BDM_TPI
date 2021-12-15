package com.bdmhpe.scraper;

import lombok.Data;

@Data
public class AuthorizationInfo {

    private Status status;

    private String accessToken;

    private String error;

    private String message;

    private AuthorizationInfo(Status status, String accessToken, String error, String message) {
        this.status = status;
        this.accessToken = accessToken;
        this.error = error;
        this.message = message;
    }

    private AuthorizationInfo(Status status) {
        this.status = status;
    }

    public static AuthorizationInfo success(String accessToken) {
        return new AuthorizationInfo(AuthorizationInfo.Status.SUCCESS, accessToken, null, null);
    }

    public static AuthorizationInfo failed() {
        return new AuthorizationInfo(AuthorizationInfo.Status.FAILED);
    }

    public static AuthorizationInfo failed(String error, String message) {
        return new AuthorizationInfo(Status.FAILED, null, error, message);
    }

    public enum Status {SUCCESS, FAILED}

    public String prettyPrint() {
        StringBuilder result = new StringBuilder();
        result.append(String.format("Auth %s", status));
        if (authSucceeded()) {
            result.append(String.format(" - Access Token: %s", accessToken));
        }
        else {
            result.append(String.format(" - Error: %s - Message: %s", error, message));
        }
        return result.toString();
    }

    private boolean authSucceeded() {
        return this.status.equals(Status.SUCCESS);
    }
}