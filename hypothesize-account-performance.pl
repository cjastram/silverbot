#!/usr/bin/perl -w

use strict;

package Account;
sub new {
    my $self = ();
    my $class = shift;

    $self->{"_value"} = shift;
    $self->{"_bids"} = [];
    $self->{"_asks"} = [];
    $self->{"_unsold"} = {};
    $self->{"_bidSize"} = 40;
    $self->{"_interval"} = 0.50;
    $self->{"_spread"} = 0.50;
    
    bless $self, $class;

    print "Starting value: $self->{_value}\n";

    return $self;
}
sub getValue {
    my( $self ) = @_;
    return $self->{_value};
}
sub setValue {
    my ($self, $value) = @_;
    $self->{_value} = $value if defined($value);
    return $self->{_value};
}
sub getAsks {
    my( $self ) = @_;
    return sort {$a <=> $b} @{$self->{_asks}};
}
sub getBids {
    my( $self ) = @_;
    return sort {$a <=> $b} @{$self->{_bids}};
}
sub bid {
    my( $self, $price ) = @_;
    $price = sprintf "%0.2f", $price;
    #print "bid $price\n";
    push @{$self->{_bids}}, $price;
}
sub ask {
    my( $self, $price ) = @_;
    $price = sprintf "%0.2f", $price;
    #print "ask $price\n";
    push @{$self->{_asks}}, $price
}
sub cancelBid {
    my( $self, $price ) = @_;
    my @bids = @{$self->{_bids}};
    $self->{_bids} = [];
    foreach my $bid (@bids) {
        if ($bid != $price) {
            $self->bid($bid);
        }
    }
}
sub cancelAsk {
    my( $self, $price ) = @_;
    my @asks = @{$self->{_asks}};
    $self->{_asks} = [];
    foreach my $ask (@asks) {
        if ($ask != $price) {
            $self->ask($ask);
        }
    }
}
sub insertBids {
    my $self = shift;
    my $ask = 0 + shift;
    my $bidSize = $self->{_bidSize};
    my $interval = $self->{_interval};
    
    my $capacity = $self->getValue();
   
    my $top = $ask;
    my $bottom = $ask;
    foreach my $bid ($self->getBids()) {
        if( $top == $ask ) {
            $top = $bid;
            $bottom = $bid;
        } elsif ($bid > $top) {
            $top = $bid;
        } elsif ($bid < $bottom) {
            $bottom = $bid;
        }
        $capacity -= ($bidSize * $bid);
    }

    # Fill in bids as the price rises
    my $ceiling = $top;
    $ceiling += $interval;
    while ($ceiling < $ask) {
        if ( not $self->{_unsold}->{"b".sprintf("%0.2f",$ceiling)}) {
            $self->bid($ceiling);
            $capacity -= $bidSize * $ceiling;
        }
        $ceiling += $interval;
    }

    # Fill in low bids, to capacity
    # TODO: Cancel bids that exceed capacity
    while ($capacity > 0) {
        $bottom -= $interval;
        if ($bottom < 5)
        {
            last;
        }
        my $cost = $bidSize * $bottom;
        if ($capacity > $cost) {
            $self->bid($bottom);
            $capacity -= $cost;
        } else {
            last;
        }
    }
}
sub tick {
    my ($self, $side, $price) = @_;
    #print "\n--> TICK: $side/$price\n";
    my $bidSize = $self->{_bidSize};
    if ($side eq "ask") {
        $self->insertBids($price);
        foreach my $bid ($self->getBids()) {
            if ($price < $bid) {
                #print "Executed bid at $bid...\n";
                $self->cancelBid($bid);
                my $cost = $bid*$bidSize;
                $cost++;
                $self->setValue($self->getValue() - $cost);

                my $askPrice = $bid+$self->{_interval};
                $self->{_unsold}->{"b".sprintf("%0.2f", $bid)} = sprintf("%0.2f", $askPrice);
                $self->{_unsold}->{"a".sprintf("%0.2f", $askPrice)} = sprintf("%0.2f", $bid);
                
                $self->ask($askPrice);
            }
        }
    } elsif ($side eq "bid") {
        foreach my $ask ($self->getAsks()) {
            if ($price > $ask) {
                #print "Executed ask at $ask...\n";
                $self->cancelAsk($ask);
                my $cost = $ask*$bidSize;
                $cost++;
                $self->setValue($self->getValue() + $cost);

                my $bidPrice = $self->{_unsold}->{"a".sprintf("%0.2f",$ask)};
                delete $self->{_unsold}->{"a".sprintf("%0.2f",$ask)};
                delete $self->{_unsold}->{"b".sprintf("%0.2f",$bidPrice)};
            }
        }
    }
}
sub close {
    my $self = shift;
    my $bidSize = $self->{_bidSize};
    foreach my $ask ($self->getAsks()) {
        $self->cancelAsk($ask);
        my $cost = $ask*$bidSize;
        $cost++;
        $self->setValue($self->getValue() + $cost);
                
        my $bidPrice = $self->{_unsold}->{"a".sprintf("%0.2f",$ask)};
        delete $self->{_unsold}->{"a".sprintf("%0.2f",$ask)};
        delete $self->{_unsold}->{"b".sprintf("%0.2f",$bidPrice)};
    }
    print "Final value: " . $self->getValue() . "\n";
}

my @data = ();
while (<>) {
    push @data, $_;
}

my $account = new Account(10000);
foreach (@data) {
    m/^([\d]+)\..*: \[(bid|ask), ([\d.]+)\]/;
    my ($timestamp, $side, $price) = ($1, $2, $3);
    $account->tick( $side, $price );
}
$account->close();

