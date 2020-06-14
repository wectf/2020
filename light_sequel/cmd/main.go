package cmd

import (
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"github.com/google/uuid"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/reflection"
	pb "light_sequel/proto"
	"log"
	"net"
	"os"
	"xorm.io/xorm"
)

var db *xorm.Engine

type Users struct {
	Id       int64
	Username string
	Password string
	Token    string
}

type UserLogs struct {
	Id     int64
	UserId int64
	Ip     string
}

type Flags struct {
	Id   int64
	Flag string `gorm:"unique;not null";json:"flag"`
}

type authServer struct{}

func (s *authServer) Login(ctx context.Context, in *pb.AuthRequest) (*pb.AuthReply, error) {
	md, _ := metadata.FromIncomingContext(ctx)
	if len(md["ip"]) == 0 {
	    // no ip provided by upstream
		return &pb.AuthReply{
			Token: "NO_IP",
			Id:    int32(-1000),
		}, nil
	}
	var u Users
	db.
		Select("token, id").
		Where("username = ? AND password = ?", in.Username, in.Password).Get(&u)
	if u.Id != 0 {
	    // create login record
		_, err := db.Insert(UserLogs{UserId: u.Id, Ip: md["ip"][0]})
		if err != nil {
			log.Fatalf("failed to create record: %v", err)
		}
	}
	return &pb.AuthReply{
		Token: u.Token,
		Id:    int32(u.Id),
	}, nil
}

func (s *authServer) Register(ctx context.Context, in *pb.AuthRequest) (*pb.AuthReply, error) {
	userTokenUUID := uuid.New()
	userToken := userTokenUUID.String()
	u := Users{
		Username: in.Username,
		Password: in.Password,
		Token:    userToken,
	}
	db.Insert(u)
	return &pb.AuthReply{
		Token: userToken,
		Id:    int32(u.Id),
	}, nil
}

type srvServer struct{}

func (s *srvServer) GetLoginHistory(ctx context.Context, _ *pb.SrvRequest) (*pb.SrvReply, error) {
	md, _ := metadata.FromIncomingContext(ctx)
	if len(md["user_token"]) == 0 {
	    // no user token provided by upstream
		return &pb.SrvReply{
			Ip: nil,
		}, nil
	}
	userToken := md["user_token"][0]
	var ul []UserLogs
	err := db.Table("user_logs AS ul").
		Select("ul.ip").
		Where(fmt.Sprintf("ul.user_id = (SELECT id FROM users AS u WHERE u.token = '%s')", userToken)).
		Find(&ul)
	if err != nil {
		log.Println(err)
	}
	// convert struct to an array
	var ips []string
	for _, v := range ul {
		ips = append(ips, v.Ip)
	}
	return &pb.SrvReply{
		Ip: ips,
	}, nil
}

func StartServer() {
	// set up db
	db, _ = xorm.NewEngine("sqlite3", "./v3.db")
	defer db.Close()
	db.Sync2(new(Users))
	db.Sync2(new(UserLogs))
	db.Sync2(new(Flags))
	db.Insert(
		Flags{Flag: os.Getenv("FLAG")},
	)
	// grpc server def
	lis, _ := net.Listen("tcp", ":1004")
	s := grpc.NewServer()
	pb.RegisterAuthServer(s, &authServer{})
	pb.RegisterSrvServer(s, &srvServer{})

	// Register reflection service on gRPC server.
	reflection.Register(s)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
