<?php
namespace Objects {
    const SALT = "SUPER_LONG_SALT@!#8f23r723i80tfubo13";
    use Events\NoteFromId;
    use Events\NoteFromToken;
    use Events\NoteInsert;
    use Events\UserLogin;
    use Events\UserFromId;
    use Events\UserNotes;
    use Events\UserRegistration;
    use Events\UserTokenLogin;
    require_once "Utils.inc";
    class User
    {
        public function __init_with_content($username, $password, $fetch_others=false)
        {
            $this->username = $username;
            $this->password = sha1(sha1($password . SALT) . SALT);
        }
        public function __init_with_id($id, $fetch_others=false)
        {
            $this->id = $id;
            if ($fetch_others){
                call(new UserFromId($this));
            }
        }
        public function __init_with_username($username)
        {
            $this->username = $username;
        }
        protected $id;
        public function get_id(){ return $this->id; }
        public function set_id($id) {$this->id = $id;}
        protected $username;
        public function get_username(){ return $this->username; }
        public function set_username($username){ $this->username = $username; }
        private $token;
        public function set_token($token) {$this->token = $token;}
        public function get_token() {return $this->token;}
        private $password;
        public function set_enc_password($password){ $this->password = $password; }
        public function get_enc_password(){ return $this->password; }
        public function __sleep() { return array("token"); }
        public function __wakeup() { call(new UserTokenLogin($this)); }
        public function __echo()
        {
            return result($this->__obj());
        }
        public function __obj(){
            return array(
                "username" => $this->username,
                "id" => $this->id,
            );
        }
        private function check_validity(){
            if (strlen($this->username) < 8)
                error("Username must be longer than 8 chars");
            if (strlen($this->username) > 12)
                error("Username must be shorter than 12 chars");
        }
        public function __login(){
            call(new UserLogin($this));
            return;
        }
        public function __register(){
            $this->check_validity();
            call(new UserRegistration($this));
            return;
        }
        public function __get_notes(){
            $note_objs = array();
            call(new UserNotes($this, $note_objs));
            return $note_objs;
        }
    }

    class Note
    {
        public function __init_with_content(User $u, $content, $id=0, $token='')
        {
            $this->id = $id;
            $this->author = $u;
            $this->content = $content;
            $this->token = $token;
        }
        public function __init_with_token($token, $fetch_others=false)
        {
            $this->token = $token;
            if ($fetch_others){
                call(new NoteFromToken($this));
            }
        }
        protected $id;
        public function get_id(){ return $this->id; }
        public function set_id($id){ $this->id = $id; }
        protected $content;
        public function get_content(){ return $this->content; }
        public function set_content($content){ $this->content = $content; }
        protected $author;
        public function get_author(){ return $this->author; }
        public function set_author($author){ $this->author = $author; }
        protected $token;
        public function get_token(){ return $this->token; }
        public function set_token($token){ $this->token = $token; }
        public function __sleep() { return array("id"); }
        public function __wakeup() { call(new NoteFromToken($this)); }
        public function __echo()
        {
            return result($this->__obj());
        }
        public function __obj()
        {
            return array(
                "id" => $this->id,
                "author_info" => array(
                    "name" => $this->author->get_username(),
                ),
                "content" => $this->content,
                "token" => $this->token,
            );
        }
        private function escape(){
            $this->content = htmlspecialchars(
                mb_convert_encoding($this->content, 'UTF-7'),
                ENT_QUOTES
            );
        }
        public function __save(){
            $this->escape();
            call(new NoteInsert($this));
        }
    }
}

namespace Events{

    use Objects\Note;
    use Objects\User;
    require_once "Utils.inc";
    class UserRegistration
    {
        private $user;
        public function __construct(User $u)
        {
            $this->user = $u;
        }

        private function prepare_stmt($cursor){
            return $cursor->prepare("INSERT INTO users(username, password, token) VALUES (?, ?, ?);");
        }

        private function generate_token(){
            return uniqid($this->user->get_username(), true) .
                uniqid($this->user->get_enc_password(), true);
        }

        public function __destruct()
        {
            $token = $this->generate_token();
            $cursor = get_cursor();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("sss", $this->user->get_username(),
                $this->user->get_enc_password(), $token);

            $stmt->execute();
            if ($stmt->error !== "")
                error("Possible username collision");
            $this->user->set_token($token);
            $this->user->set_id($stmt->insert_id);
        }
    }

    class UserLogin
    {
        private $user;
        public function __construct(User $u)
        {
            $this->user = $u;
        }

        private function prepare_stmt($cursor){
            return $cursor->prepare("SELECT id, password, token FROM users WHERE username=?;");

        }

        public function __destruct()
        {
            $cursor = get_cursor();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("s", $this->user->get_username());
            $stmt->execute();
            $stmt->store_result();
            $stmt->bind_result($id, $password, $token);
            if ($stmt->num_rows == 0)
                error("No such user");
            $stmt->fetch();
            if ($password !== $this->user->get_enc_password())
                error("Wrong password");
            $this->user->set_id($id);
            $this->user->set_token($token);
        }
    }

    class UserTokenLogin
    {
        private $user;
        public function __construct(User $u)
        {
            $this->user = $u;
        }

        private function prepare_stmt($cursor){
            return $cursor->prepare("SELECT id, username FROM users WHERE token=?;");

        }

        public function __destruct()
        {
            $cursor = get_cursor();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("s", $this->user->get_token());
            $stmt->execute();
            $stmt->store_result();
            $stmt->bind_result($id, $username);
            if ($stmt->num_rows == 0)
                error("Wrong Token");
            $stmt->fetch();
            $this->user->set_id($id);
            $this->user->set_username($username);
        }
    }

    class UserFromId
    {
        private $user;
        public function __construct(User $u)
        {
            $this->user = $u;
        }

        private function prepare_stmt($cursor){
            return $cursor->prepare("SELECT username FROM users WHERE id=?;");

        }

        public function __destruct()
        {
            $cursor = get_cursor();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("i", $this->user->get_id());
            $stmt->execute();
            $stmt->store_result();
            $stmt->bind_result($username);
            if ($stmt->num_rows == 0)
                error("No such user");
            $stmt->fetch();
            $this->user->set_username($username);
        }
    }

    class UserNotes
    {
        private $user, $notes;
        public function __construct(User $u, &$ns)
        {
            $this->user = $u;
            $this->notes = &$ns;
        }
        private function prepare_stmt($cursor){
            return $cursor->prepare("SELECT id, content, token FROM notes WHERE author_name=? LIMIT 20;");
        }

        public function __destruct()
        {
            $cursor = get_cursor();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("s", $this->user->get_username());
            $stmt->execute();
            $stmt->store_result();
            $stmt->bind_result($id, $content, $token);
            while ($stmt->fetch()){
                $note_obj = new Note();
                $note_obj->__init_with_content($this->user, $content, $id, $token);
                $this->notes[] = $note_obj->__obj();
            }
        }
    }

    class NoteFromToken
    {
        private $note;
        public function __construct(Note $n)
        {
            $this->note = $n;
        }

        private function prepare_stmt($cursor){
            return $cursor->prepare("SELECT id, content, author_name FROM notes WHERE token=?;");
        }

        public function __destruct()
        {
            $cursor = get_cursor();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("s", $this->note->get_token());
            $stmt->execute();
            $stmt->store_result();
            $stmt->bind_result($id, $content, $author_name);
            if ($stmt->num_rows == 0)
                error("No such note");
            $stmt->fetch();
            $this->note->set_content($content);
            $author_obj = new User();
            $author_obj->__init_with_username($author_name);
            $this->note->set_author($author_obj);
            $this->note->set_id($id);
        }
    }

    class NoteInsert
    {
        private $note;
        public function __construct(Note $n)
        {
            $this->note = $n;
        }

        private function prepare_stmt($cursor){
            return $cursor->prepare("INSERT INTO notes(content, author_name, token) VALUES (?, ?, ?);");
        }

        private function generate_token(){
            return uniqid(sha1($this->note->get_content()), true) .
                uniqid($this->note->get_author()->get_id(), true);
        }

        public function __destruct()
        {
            $cursor = get_cursor();
            $token = $this->generate_token();
            $stmt = $this->prepare_stmt($cursor);
            $stmt->bind_param("sss", $this->note->get_content(),
                $this->note->get_author()->get_username(), $token);
            $stmt->execute();
            if ($stmt->error !== "")
                error("Note too long, chatterbox... 500 chars allowed");
            $this->note->set_id($stmt->insert_id);
            $this->note->set_token($token);
        }
    }
}

