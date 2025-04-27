package main

import (
	"context"
	"log"
	"net"

	pb "github.com/Yisustxz/cen-project/backend/internal/service"
	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedGameServiceServer
}

func (s *server) SendInput(ctx context.Context, in *pb.PlayerInput) (*pb.GameState, error) {
	log.Printf("Received input from player %s: %s", in.PlayerId, in.Action)
	return &pb.GameState{Message: "Action received: " + in.Action}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterGameServiceServer(s, &server{})
	log.Println("Server is running on port 50051...")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
