export class User {
    constructor(id, username, password) {
        this.id = id;
        this.username = username;
        this.password = password;
    }

    static toJson(user) {
        return {
            id: user.id,
            username: user.username,
            password: user.password
        };
    }
}
